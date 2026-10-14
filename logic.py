import random                                             # for random code generation
import time                                               # time module for countdown and timestamps
from datetime import datetime, timezone, timedelta       # for date and time calculations
import urllib.request                                     # for ip geolocation api calls
import json                                              # for parsing api response
import streamlit as st                                    # streamlit for shared cache_resource
from csv_handler import read_present_students, append_attendance_to_csv # csv helper functions
from qr_code import create_random_token                  # token generation helper
import scheduler                                          # backend CPU scheduling engine


def get_ist_now():
    utc_now = datetime.now(timezone.utc)                 # get current UTC time
    ist_tz = timezone(timedelta(hours=5, minutes=30))     # Indian Standard Time (UTC+5:30)
    return utc_now.astimezone(ist_tz)                    # convert to IST


def generate_auth_code():
    prefix = "".join(random.choices(["A", "B", "C", "D"], k=2)) # 2 letters (A-D)
    suffix = "".join(random.choices("0123456789", k=4))         # 4 digits
    return f"{prefix}{suffix}"                                  # e.g. AB1282


# IP security functions have been moved to ip_security.py
import ip_security


TEACHER_PROFILES = {
    "123456": {
        "name": "Prof. Deepthi Rapeti",
        "subject": "COOS",
        "department": "AIML",
        "classes": ["AIML A", "AIML B", "AIML C", "AIML D"]
    }
}


def verify_teacher_pin(pin):
    clean_pin = str(pin).strip()
    return TEACHER_PROFILES.get(clean_pin, None)


def get_default_time_slot():
    now = get_ist_now()                                   # current IST datetime
    hour = now.hour                                       # current hour
    minute = now.minute                                   # current minute

    # Nearest 30-min round (e.g. 3:25 -> ends 3:30, starts 2:30)
    if 15 <= minute < 45:
        end_h, end_m = hour, 30
    elif minute >= 45:
        end_h, end_m = (hour + 1) % 24, 0
    else:  # 0 to 14
        end_h, end_m = (hour + 1) % 24, 0

    start_h = (end_h - 1) % 24
    start_m = end_m

    dummy = now.replace(second=0, microsecond=0)
    start_dt = dummy.replace(hour=start_h, minute=start_m)
    end_dt = dummy.replace(hour=end_h, minute=end_m)
    return start_dt.strftime("%I:%M %p"), end_dt.strftime("%I:%M %p")


@st.cache_resource
def get_system_state():
    default_start, default_end = get_default_time_slot()  # get initial nearest 30-min slot
    return {
        "active": False,                                  # session active flag
        "session_id": "",                                 # unique lecture session id
        "faculty_name": "Prof. Deepthi Rapeti",           # logged in faculty name
        "class_name": "AIML A",                           # selected class (AIML A/B/C/D)
        "subject": "COOS",                                # Prof. Deepthi Rapeti teaches COOS
        "date": datetime.now().strftime("%Y-%m-%d"),      # today's date
        "lecture_time": f"{default_start} - {default_end}", # default lecture slot
        "token": "",                                      # current active 10s token
        "created_time": 0.0,                              # token creation timestamp
        "expiry_time": 0.0,                               # token expiry timestamp
        "scheduling_algo": "Round Robin",                 # backend CPU scheduling algorithm
        "time_quantum": 2,                                # round robin time quantum (ms)
        "processed_queue": [],                            # backend queue of scheduled requests
        "marked_ips": {},                                 # marked ips
        "session_present_rolls": []                       # rolls marked in this specific active session
    }                                                     # shared state dictionary


def start_session(class_name, subject, date_str, time_slot, algo="Round Robin", quantum=2, faculty_name="Prof. Deepthi Rapeti"):
    state = get_system_state()                            # get shared memory state
    token = create_random_token()                         # generate first random token
    now = time.time()                                     # current time in seconds

    state["active"] = True                                # mark session active
    state["session_id"] = f"{class_name}_{subject}_{date_str}_{time_slot}_{int(now)}" # unique session id
    state["faculty_name"] = faculty_name                 # save faculty name
    state["class_name"] = class_name                      # save class name
    state["subject"] = subject                            # save subject
    state["date"] = date_str                              # save date string
    state["lecture_time"] = time_slot                     # save lecture time slot
    state["token"] = token                                # save active token
    state["created_time"] = now                           # record start time
    state["expiry_time"] = now + 20.0                     # first QR code strictly expires in 20 seconds
    state["is_first_qr"] = True                           # mark first QR flag
    state["valid_tokens"] = {token: now + 20.0}           # map of valid tokens and their expiry
    state["scheduling_algo"] = algo                       # backend algorithm (Round Robin / FCFS)
    state["time_quantum"] = quantum                       # set time quantum
    state["processed_queue"] = []                         # reset live queue for new session
    state["marked_ips"] = {}                              # reset IP tracking for new session
    state["session_present_rolls"] = []                   # reset active session roll list
    return token                                          # return generated token


def stop_session():
    state = get_system_state()                            # get shared memory state
    state["active"] = False                               # mark session inactive
    state["token"] = ""                                   # clear token
    state["expiry_time"] = 0.0                            # clear expiry
    state["is_first_qr"] = True                           # reset for next session
    state["valid_tokens"] = {}                            # clear tokens
    state["session_present_rolls"] = []                   # clear active session rolls


def check_and_refresh_token():
    state = get_system_state()                            # get shared state
    now = time.time()                                     # current timestamp
    remaining = int(state.get("expiry_time", 0) - now)     # calculate seconds remaining

    if "valid_tokens" not in state:
        state["valid_tokens"] = {}

    # Clean up tokens older than 45 seconds from memory
    state["valid_tokens"] = {t: exp for t, exp in state["valid_tokens"].items() if now <= exp + 45.0}

    if remaining <= 0 or not state.get("token"):          # if expired or token empty
        is_first = state.get("is_first_qr", False)
        duration = 20.0 if is_first else 10.0            # 20s if first QR, 10s for subsequent
        new_token = create_random_token()                 # generate brand new token
        state["token"] = new_token
        state["created_time"] = now                       # reset creation time
        state["expiry_time"] = now + duration             # set expiry time
        state["valid_tokens"][new_token] = state["expiry_time"]
        state["is_first_qr"] = False                      # all next refreshes will be 10s
        remaining = int(duration)                         # reset countdown to duration

    return remaining                                      # return countdown seconds


def verify_scanned_token(scanned_token):
    state = get_system_state()                            # get shared state
    now = time.time()                                     # current timestamp

    if not state.get("active"):                           # if teacher stopped session
        return "SESSION_NOT_ACTIVE"                       # session inactive

    # Check against current active token
    if scanned_token == state.get("token"):
        if now <= state.get("expiry_time", 0) + 5.0:      # 5s network grace
            return "TOKEN_VALID"
        return "TOKEN_EXPIRED"

    # Check against recent tokens (gives student mobile browser 20s grace to load form)
    valid_tokens = state.get("valid_tokens", {})
    if scanned_token in valid_tokens:
        token_exp = valid_tokens[scanned_token]
        if now <= token_exp + 20.0:
            return "TOKEN_VALID"

    return "TOKEN_EXPIRED"                                # expired qr code


def process_attendance_submission(class_name, subject, date_str, time_slot, roll_number, client_ip=None):
    if not roll_number:                                   # if student entered blank roll no
        return "EMPTY_ROLL_NUMBER", None                  # reject empty input

    state = get_system_state()                            # fetch shared system state

    # -------------------------------------------------------------------------
    # [TEACHER DEMO: 1 IP = 1 ATTENDANCE RESTRICTION]
    # Uncomment lines below to block multiple submissions from the same IP:
    # -------------------------------------------------------------------------
    # if client_ip and ip_security.is_ip_already_used(state, client_ip):
    #     prev = state.get("marked_ips", {}).get(client_ip, "Unknown")
    #     return f"IP_ALREADY_USED:{prev}", None

    # Check active in-memory session rolls
    if roll_number in state.get("session_present_rolls", []):
        return "ALREADY_MARKED", None

    # Check CSV matching this specific lecture time slot
    present = read_present_students(class_name, subject, date_str, time_slot)
    if roll_number in present:                            # duplicate check for this lecture
        return "ALREADY_MARKED", None                     # already marked present

    algo = state["scheduling_algo"]                       # active algorithm (FCFS or Round Robin)
    q = state["time_quantum"]                             # time quantum

    # Execute backend CPU Scheduling on incoming request
    schedule_info = scheduler.schedule_request(algo, roll_number, state["processed_queue"], q) # run scheduler
    state["processed_queue"].append(schedule_info)        # record in live request queue

    # Record in active session list
    if "session_present_rolls" not in state:
        state["session_present_rolls"] = []
    state["session_present_rolls"].append(roll_number)

    # -------------------------------------------------------------------------
    # Record IP mapping (Uncomment line below to track IPs for teacher demo):
    # -------------------------------------------------------------------------
    # if client_ip:
    #     ip_security.register_ip_submission(state, client_ip, roll_number)

    append_attendance_to_csv(class_name, subject, date_str, time_slot, roll_number) # save to csv
    return "SUCCESS", schedule_info                       # return success with process metrics

