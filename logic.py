import time                                               # time module for token expiry calculation
from datetime import datetime, timezone, timedelta       # date and timezone calculations
import streamlit as st                                    # streamlit cache_resource for shared memory
import config                                             # faculty profiles and timing configs
from csv_handler import read_present_students, append_attendance_to_csv # csv operations
from qr_code import create_random_token                  # 6-character random token generator


def get_ist_now():
    utc_now = datetime.now(timezone.utc)                 # get current utc datetime
    ist_tz = timezone(timedelta(hours=5, minutes=30))     # ist timezone offset (utc+5:30)
    return utc_now.astimezone(ist_tz)                    # convert to indian standard time


def verify_teacher_pin(pin):
    clean_pin = str(pin).strip()                          # sanitize entered pin
    return config.FACULTY_PROFILES.get(clean_pin, None)  # match pin in faculty config profiles


def get_default_time_slot():
    now = get_ist_now()                                   # current ist time
    hour = now.hour                                       # hour
    minute = now.minute                                   # minute

    if 15 <= minute < 45:
        end_h, end_m = hour, 30                          # round to nearest half-hour mark
    elif minute >= 45:
        end_h, end_m = (hour + 1) % 24, 0                # round up to next hour mark
    else:
        end_h, end_m = (hour + 1) % 24, 0                # round to hour mark

    start_h = (end_h - 1) % 24                           # 1 hour prior lecture start
    start_m = end_m                                       # matching minute

    base_dt = now.replace(second=0, microsecond=0)        # zero out seconds
    start_dt = base_dt.replace(hour=start_h, minute=start_m) # start datetime
    end_dt = base_dt.replace(hour=end_h, minute=end_m)   # end datetime

    return start_dt.strftime("%I:%M %p"), end_dt.strftime("%I:%M %p") # formatted 12-hour slot


@st.cache_resource
def get_system_state():
    default_start, default_end = get_default_time_slot()  # get initial lecture time slot
    return {
        "active": False,                                  # session active indicator
        "session_id": "",                                 # unique lecture session id
        "faculty_name": "Ms. Seema Nagrani",              # default logged-in faculty
        "class_name": "AIML C",                           # default class
        "subject": "PPCA",                                # default subject
        "date": datetime.now().strftime("%Y-%m-%d"),      # today's date string
        "lecture_time": f"{default_start} - {default_end}", # lecture slot string
        "token": "",                                      # current active qr token
        "created_time": 0.0,                              # token start timestamp
        "expiry_time": 0.0,                               # token expiry timestamp
        "qr_count": 0,                                    # active qr generation count
        "valid_tokens": {},                               # history of recent tokens with expiry
        "marked_ips": {},                                 # submitted ip map
        "session_present_rolls": []                       # rolls marked in active session
    }


def start_session(class_name, subject, date_str, time_slot, faculty_name="Ms. Seema Nagrani"):
    state = get_system_state()                            # shared state memory
    token = create_random_token()                         # initial random token
    now = time.time()                                     # current timestamp

    state["active"] = True                                # activate live session
    state["session_id"] = f"{class_name}_{subject}_{date_str}_{time_slot}_{int(now)}" # unique session id
    state["faculty_name"] = faculty_name                 # store faculty name
    state["class_name"] = class_name                      # store class name
    state["subject"] = subject                            # store subject
    state["date"] = date_str                              # store lecture date
    state["lecture_time"] = time_slot                     # store lecture slot
    state["token"] = token                                # set active token
    state["created_time"] = now                           # record start time
    state["expiry_time"] = now + config.INITIAL_QR_DURATION # initial QR strictly 20 seconds
    state["qr_count"] = 1                                 # mark initial QR
    state["valid_tokens"] = {token: state["expiry_time"]} # store token in valid map
    state["marked_ips"] = {}                              # reset ip map
    state["session_present_rolls"] = []                   # reset present roll list
    return token                                          # return generated token


def stop_session():
    state = get_system_state()                            # shared state memory
    state["active"] = False                               # mark session inactive
    state["token"] = ""                                   # clear active token
    state["expiry_time"] = 0.0                            # clear expiry
    state["qr_count"] = 0                                 # reset qr count
    state["valid_tokens"] = {}                            # clear token map
    state["session_present_rolls"] = []                   # reset active rolls


def check_and_refresh_token():
    state = get_system_state()                            # shared state memory
    now = time.time()                                     # current timestamp
    remaining = int(state.get("expiry_time", 0) - now)     # calculate seconds left

    if "valid_tokens" not in state:
        state["valid_tokens"] = {}                        # ensure valid tokens map exists

    # Prune tokens older than 45 seconds from memory
    state["valid_tokens"] = {t: exp for t, exp in state["valid_tokens"].items() if now <= exp + 45.0}

    if remaining <= 0 or not state.get("token"):          # initial QR expired or token empty
        duration = config.REGULAR_QR_DURATION             # all refreshed QR codes are strictly 10 seconds
        new_token = create_random_token()                 # create fresh token
        state["token"] = new_token                        # assign active token
        state["created_time"] = now                       # record timestamp
        state["expiry_time"] = now + duration             # set 10s expiration
        state["valid_tokens"][new_token] = state["expiry_time"] # record in valid map
        state["qr_count"] = state.get("qr_count", 1) + 1  # increment refreshed qr count
        remaining = int(duration)                         # reset countdown to 10s

    return remaining                                      # return countdown seconds


def verify_scanned_token(scanned_token):
    state = get_system_state()                            # shared state memory
    now = time.time()                                     # current timestamp

    if not state.get("active"):
        return "SESSION_NOT_ACTIVE"                       # session stopped by teacher

    if scanned_token == state.get("token"):               # direct match with active token
        if now <= state.get("expiry_time", 0) + 5.0:      # 5s network grace buffer
            return "TOKEN_VALID"                          # token accepted
        return "TOKEN_EXPIRED"                            # token timed out

    valid_tokens = state.get("valid_tokens", {})          # check recent token history
    if scanned_token in valid_tokens:
        token_expiry = valid_tokens[scanned_token]        # get token expiry timestamp
        if now <= token_expiry + config.MOBILE_GRACE_PERIOD: # 20s mobile loading grace buffer
            return "TOKEN_VALID"                          # token accepted

    return "TOKEN_EXPIRED"                                # expired or invalid


def process_attendance_submission(class_name, subject, date_str, time_slot, roll_number, client_ip=None):
    if not roll_number:
        return "EMPTY_ROLL_NUMBER"                        # reject blank input

    state = get_system_state()                            # shared state memory

    if roll_number in state.get("session_present_rolls", []): # duplicate in memory
        return "ALREADY_MARKED"

    already_present = read_present_students(class_name, subject, date_str, time_slot) # duplicate in csv
    if roll_number in already_present:
        return "ALREADY_MARKED"

    if "session_present_rolls" not in state:
        state["session_present_rolls"] = []               # ensure list exists
    state["session_present_rolls"].append(roll_number)    # add to live session rolls

    append_attendance_to_csv(class_name, subject, date_str, time_slot, roll_number) # write to csv
    return "SUCCESS"                                      # return success
