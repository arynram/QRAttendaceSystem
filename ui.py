import time                                               # time module for countdown and refresh
from datetime import datetime                             # date and time formatting
import streamlit as st                                    # streamlit web framework
import config                                             # system settings and faculty profiles
import logic                                              # core attendance business logic
import qr_code                                            # qr code generator and network ip
import csv_handler                                        # csv database handler
import pdf_generator                                      # pdf report generator


def get_client_ip():
    headers = getattr(st.context, "headers", {})          # fetch request headers
    xff = headers.get("x-forwarded-for") or headers.get("X-Forwarded-For") # proxy header
    if xff:
        return xff.split(",")[0].strip()                  # extract client ip
    cf_ip = headers.get("cf-connecting-ip") or headers.get("CF-Connecting-IP") # cloudflare header
    if cf_ip:
        return cf_ip.strip()                              # extract cloudflare client ip
    ctx_ip = getattr(st.context, "ip_address", None)      # native streamlit context
    if ctx_ip:
        return str(ctx_ip).strip()                        # extract context ip
    return None


def get_base_url(server_ip, server_port="8501"):
    headers = getattr(st.context, "headers", {})          # request headers
    host = headers.get("host") or headers.get("Host")     # host domain or ip
    if host and "localhost" not in host and "127.0.0.1" not in host:
        proto = headers.get("x-forwarded-proto", "https" if "streamlit.app" in host else "http") # protocol
        return f"{proto}://{host}"                        # remote or cloud base url
    return f"http://{server_ip}:{server_port}"            # local network url


def render_smartboard_pin_screen():
    if "entered_pin" not in st.session_state:
        st.session_state["entered_pin"] = ""              # initialize pin buffer
    if "pin_error" not in st.session_state:
        st.session_state["pin_error"] = ""                # initialize pin error

    st.markdown("<h1>Faculty Login</h1>", unsafe_allow_html=True) # basic html title
    st.markdown("<p>Enter 6-digit faculty PIN to unlock attendance portal.</p>", unsafe_allow_html=True) # instruction
    st.markdown("<hr>", unsafe_allow_html=True)           # horizontal line

    entered = st.session_state["entered_pin"]             # entered digits
    masked = "".join(["● " for _ in entered]) + "".join(["- " for _ in range(6 - len(entered))]) # masked view
    st.markdown(f"<h3>PIN: {masked.strip()}</h3>", unsafe_allow_html=True) # basic html pin text

    if st.session_state["pin_error"]:
        st.markdown(f"<p><b>Error:</b> {st.session_state['pin_error']}</p>", unsafe_allow_html=True) # basic error text

    keypad = [                                            # 3x4 numeric keypad
        ["1", "2", "3"],
        ["4", "5", "6"],
        ["7", "8", "9"],
        ["Clear", "0", "Unlock"]
    ]

    for row in keypad:
        cols = st.columns(3)                              # 3 columns per row
        for i, key in enumerate(row):
            with cols[i]:
                if key == "Unlock":
                    if st.button("Unlock", key="btn_unlock", use_container_width=True):
                        prof = logic.verify_teacher_pin(st.session_state["entered_pin"]) # check pin
                        if prof:
                            st.session_state["smartboard_unlocked"] = True # unlock
                            st.session_state["teacher_profile"] = prof    # save profile
                            st.session_state["pin_error"] = ""            # clear error
                            st.rerun()
                        else:
                            st.session_state["pin_error"] = "Invalid PIN. Please try again." # wrong pin
                            st.rerun()
                elif key == "Clear":
                    if st.button("Clear", key="btn_clear", use_container_width=True):
                        st.session_state["entered_pin"] = ""      # clear pin input
                        st.session_state["pin_error"] = ""        # clear error
                        st.rerun()
                else:
                    if st.button(key, key=f"btn_{key}", use_container_width=True):
                        if len(st.session_state["entered_pin"]) < 6:
                            st.session_state["entered_pin"] += key # append number
                            st.session_state["pin_error"] = ""     # clear error
                            st.rerun()


def render_teacher_screen():
    state = logic.get_system_state()                      # fetch shared state

    if not state["active"] and not st.session_state.get("smartboard_unlocked", False):
        render_smartboard_pin_screen()                    # show pin lock if not unlocked
        return

    profile = st.session_state.get("teacher_profile", config.FACULTY_PROFILES["234567"]) # default to seema ma'am
    faculty_name = profile.get("name", "Ms. Seema Nagrani") # teacher name
    faculty_sub = profile.get("subject", "PPCA")          # subject code
    faculty_dept = profile.get("department", "AIML")      # department
    faculty_classes = profile.get("classes", ["AIML C"])  # class list

    server_ip = qr_code.get_laptop_ip()                  # local network ip
    server_port = "8501"                                  # local port
    ist_now = logic.get_ist_now()                         # current ist time
    auto_start, auto_end = logic.get_default_time_slot()  # nearest 30-min slot
    auto_slot = f"{auto_start} - {auto_end}"              # default slot string

    # Header section using basic HTML
    st.markdown(f"<h2>{faculty_name}</h2>", unsafe_allow_html=True) # basic heading
    st.markdown(f"<p><b>Subject:</b> {faculty_sub} | <b>Department:</b> {faculty_dept}</p>", unsafe_allow_html=True) # details
    if not state["active"]:
        if st.button("Logout"):
            st.session_state["smartboard_unlocked"] = False # lock portal
            st.session_state["entered_pin"] = ""          # clear pin
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)           # horizontal divider line

    # Case 1: Session not active (Setup & Past Records)
    if not state["active"]:
        tab_start, tab_past = st.tabs(["Start Attendance", "Past Records"]) # tabs

        with tab_start:
            st.markdown("<p><b>Select Class:</b></p>", unsafe_allow_html=True) # class label
            class_choice = st.radio("Select Class", faculty_classes, horizontal=True, label_visibility="collapsed") # class radio
            st.markdown(f"<p><b>Subject:</b> {faculty_sub}</p>", unsafe_allow_html=True) # subject text

            col_d1, col_d2 = st.columns(2)                # date and time columns
            with col_d1:
                st.markdown("<p><b>Lecture Date:</b></p>", unsafe_allow_html=True)
                sel_date = st.date_input("Date", value=ist_now.date(), label_visibility="collapsed") # date picker
                sel_date_str = sel_date.strftime("%Y-%m-%d") # formatted date
            with col_d2:
                chosen_slot = st.session_state.get("chosen_slot", auto_slot) # current slot
                st.markdown("<p><b>Lecture Time Slot:</b></p>", unsafe_allow_html=True)
                sel_slot = st.text_input("Time Slot", value=chosen_slot, label_visibility="collapsed") # slot input

            col_p1, col_p2 = st.columns(2)                # time preset buttons
            alt_h = ist_now.hour % 24                     # hour
            alt_slot = f"{ist_now.replace(hour=alt_h, minute=0).strftime('%I:%M %p')} - {ist_now.replace(hour=(alt_h+1)%24, minute=0).strftime('%I:%M %p')}"
            with col_p1:
                if st.button(f"Auto Time: {auto_slot}", use_container_width=True):
                    st.session_state["chosen_slot"] = auto_slot # set auto slot
                    st.rerun()
            with col_p2:
                if st.button(f"Exact Hour: {alt_slot}", use_container_width=True):
                    st.session_state["chosen_slot"] = alt_slot # set hour slot
                    st.rerun()

            st.write("")                                  # spacing
            if st.button("Start Attendance Session", use_container_width=True):
                logic.start_session(class_choice, faculty_sub, sel_date_str, sel_slot, faculty_name) # start
                st.rerun()

        with tab_past:
            past_sessions = csv_handler.get_subject_sessions(faculty_sub) # get past records
            if past_sessions:
                st.markdown(f"<h3>Past Attendance Records ({faculty_sub})</h3>", unsafe_allow_html=True)
                for (c, d, t), rolls in sorted(past_sessions.items(), reverse=True):
                    pdf_data = pdf_generator.generate_attendance_pdf(c, faculty_sub, d, t, rolls, faculty_name) # pdf
                    st.markdown(f"<p><b>Class:</b> {c} | <b>Date:</b> {d} | <b>Time:</b> {t} | <b>Present:</b> {len(rolls)}</p>", unsafe_allow_html=True)
                    st.download_button(
                        label=f"Download PDF ({c} - {d})",
                        data=pdf_data,
                        file_name=f"{faculty_sub}_{c}_{d}.pdf",
                        mime="application/pdf",
                        key=f"dl_{c}_{d}_{t}"
                    )                                     # download button
                    st.markdown("<hr>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p>No past attendance sessions recorded for {faculty_sub} yet.</p>", unsafe_allow_html=True) # empty notice
        return

    # Case 2: Session Active (Live Rolling QR Code)
    seconds_left = logic.check_and_refresh_token()        # countdown seconds
    base_url = get_base_url(server_ip, server_port)       # access url
    qr_url = f"{base_url}/?token={state['token']}"        # student attendance link
    qr_bytes = qr_code.generate_qr_image(qr_url)         # qr image bytes

    active_class = state["class_name"]                    # live class
    active_sub = state["subject"]                         # live subject
    active_date = state["date"]                           # live date
    active_slot = state["lecture_time"]                   # live slot
    present = csv_handler.read_present_students(active_class, active_sub, active_date, active_slot) # present list

    # Live lecture details using basic HTML
    st.markdown(f"<h2>Live Attendance: {active_class} — {active_sub}</h2>", unsafe_allow_html=True) # heading
    st.markdown(f"<p><b>Faculty:</b> {faculty_name} | <b>Date:</b> {active_date} | <b>Time Slot:</b> {active_slot}</p>", unsafe_allow_html=True)
    st.markdown(f"<h3>Total Students Marked: {len(present)}</h3>", unsafe_allow_html=True) # count

    col_l, col_qr, col_r = st.columns([1, 2, 1])          # center qr layout
    with col_qr:
        st.image(qr_bytes, use_container_width=True)      # display qr code image
        countdown_label = "Initial QR Code (20s):" if state.get("qr_count", 1) <= 1 else "QR refreshes in:" # label
        st.markdown(f"<p style='text-align: center;'><b>{countdown_label} {seconds_left}s</b></p>", unsafe_allow_html=True) # countdown text

    col_stop, col_pdf = st.columns(2)                     # action buttons
    with col_stop:
        if st.button("Stop Attendance", use_container_width=True):
            logic.stop_session()                          # stop session
            st.rerun()
    with col_pdf:
        pdf_data = pdf_generator.generate_attendance_pdf(active_class, active_sub, active_date, active_slot, present, faculty_name) # compile pdf
        st.download_button(
            label="Download PDF Report",
            data=pdf_data,
            file_name=f"Attendance_{active_class}_{active_sub}_{active_date}.pdf",
            mime="application/pdf",
            use_container_width=True
        )                                                 # download report

    if present:
        roll_text = ", ".join([f"Roll {r}" for r in present])
        st.markdown(f"<p><b>Present Students ({len(present)}):</b> {roll_text}</p>", unsafe_allow_html=True) # present list text

    time.sleep(1)                                         # 1 second wait
    st.rerun()                                            # auto rerun for countdown


def render_student_screen(scanned_token):
    client_ip = get_client_ip()                           # client ip
    state = logic.get_system_state()                      # system state
    current_session_id = state.get("session_id", f"{state['class_name']}_{state['subject']}_{state['date']}_{state['lecture_time']}") # session id

    st.markdown("<h1>Student Attendance</h1>", unsafe_allow_html=True) # basic title
    st.markdown("<hr>", unsafe_allow_html=True)           # horizontal line

    if st.session_state.get("submitted_session_id") == current_session_id and "submitted_roll" in st.session_state:
        already_roll = st.session_state["submitted_roll"]  # recorded roll
        st.markdown("<h3>Attendance Recorded</h3>", unsafe_allow_html=True) # heading
        st.markdown(f"<p>Your attendance for <b>Roll No. {already_roll}</b> has been recorded.</p>", unsafe_allow_html=True) # notice
        return

    token_status = logic.verify_scanned_token(scanned_token) # verify token

    if token_status == "SESSION_NOT_ACTIVE":
        st.markdown("<p><b>Attendance session is not currently active.</b></p>", unsafe_allow_html=True) # inactive
        return

    now = time.time()                                     # timestamp
    if token_status == "TOKEN_VALID":
        st.session_state["token_time"] = now              # record scan time
        st.session_state["valid_token"] = scanned_token   # save valid token

    is_valid = (
        st.session_state.get("valid_token") == scanned_token
        and (now - st.session_state.get("token_time", 0)) <= 60
    )                                                     # 60s typing buffer

    if not is_valid:
        st.markdown("<p><b>QR Code expired. Please scan the latest QR code from the screen.</b></p>", unsafe_allow_html=True) # expired
        return

    class_name = state["class_name"]                      # class name
    subject = state["subject"]                            # subject
    date_str = state["date"]                              # date
    time_slot = state["lecture_time"]                     # time slot
    faculty = state.get("faculty_name", "Ms. Seema Nagrani") # faculty name

    st.markdown(f"<p><b>Class:</b> {class_name} | <b>Subject:</b> {subject}</p>", unsafe_allow_html=True) # details
    st.markdown(f"<p><b>Faculty:</b> {faculty} | <b>Date:</b> {date_str} ({time_slot})</p>", unsafe_allow_html=True) # details

    with st.form("student_form"):
        st.markdown("<p><b>Enter Your Roll Number:</b></p>", unsafe_allow_html=True)
        roll_no = st.text_input("Roll Number", placeholder="e.g. 39", label_visibility="collapsed") # input
        submit = st.form_submit_button("Submit Attendance", use_container_width=True) # submit

        if submit:
            clean_roll = roll_no.strip()                  # sanitize input
            res = logic.process_attendance_submission(class_name, subject, date_str, time_slot, clean_roll, client_ip) # submit

            if res == "EMPTY_ROLL_NUMBER":
                st.markdown("<p><b>Error:</b> Please enter your roll number.</p>", unsafe_allow_html=True)
            elif res == "ALREADY_MARKED":
                st.markdown(f"<p><b>Notice:</b> Roll No. {clean_roll} is already marked for this lecture.</p>", unsafe_allow_html=True)
            elif res == "SUCCESS":
                st.session_state["submitted_session_id"] = current_session_id # save session submission
                st.session_state["submitted_roll"] = clean_roll # save submitted roll
                st.rerun()


def render_app():
    st.set_page_config(                                   # page configuration
        page_title="Smart Attendance",
        page_icon="📋",
        layout="centered"
    )

    token = st.query_params.get("token")                 # check token query parameter
    if token:
        render_student_screen(token)                      # render student form
    else:
        render_teacher_screen()                           # render teacher dashboard
