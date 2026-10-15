import time, streamlit as st                              # standard & ui libraries
import config, logic, qr_code, csv_handler, pdf_generator # app modules


def get_base_url():
    h = getattr(st.context, "headers", {}).get("host")    # get request host
    return f"https://{h}" if h and "localhost" not in h else f"http://{qr_code.get_laptop_ip()}:8501"


def render_smartboard_pin_screen():
    st.markdown("<h1>Faculty Login</h1><p>Enter 6-digit PIN to unlock.</p><hr>", unsafe_allow_html=True)
    pin = st.text_input("Enter 6-digit PIN:", type="password") # pin input
    if st.button("Unlock"):
        prof = logic.verify_teacher_pin(pin)              # verify faculty pin
        if prof:
            st.session_state.update(smartboard_unlocked=True, teacher_profile=prof)
            st.rerun()
        st.markdown("<p><b>Error:</b> Invalid PIN.</p>", unsafe_allow_html=True) # error msg


def render_teacher_screen():
    state = logic.get_system_state()                      # fetch session state
    if not state["active"] and not st.session_state.get("smartboard_unlocked"):
        return render_smartboard_pin_screen()             # show login if locked

    prof = st.session_state.get("teacher_profile", config.FACULTY_PROFILES["234567"])
    name, sub = prof.get("name", "Ms. Seema Nagrani"), prof.get("subject", "PPCA")
    st.markdown(f"<h2>{name}</h2><p><b>Subject:</b> {sub} | <b>Dept:</b> {prof.get('department', 'AIML')}</p>", unsafe_allow_html=True)
    if not state["active"] and st.button("Logout"):
        st.session_state["smartboard_unlocked"] = False   # lock portal
        st.rerun()
    st.markdown("<hr>", unsafe_allow_html=True)           # divider

    if not state["active"]:
        t1, t2 = st.tabs(["Start Attendance", "Past Records"]) # navigation tabs
        with t1:
            c = st.radio("Class:", prof.get("classes", ["AIML C"]), horizontal=True)
            d = st.date_input("Date:", value=logic.get_ist_now().date()).strftime("%Y-%m-%d")
            s = st.text_input("Time Slot:", value=f"{logic.get_default_time_slot()[0]} - {logic.get_default_time_slot()[1]}")
            if st.button("Start Attendance Session"):
                logic.start_session(c, sub, d, s, name)   # initialize session
                st.rerun()
        with t2:
            past = csv_handler.get_subject_sessions(sub)  # fetch past sessions
            if not past:
                st.markdown(f"<p>No past records recorded for {sub} yet.</p>", unsafe_allow_html=True)
            for (pc, pd, pt), rolls in sorted(past.items(), reverse=True):
                pdf = pdf_generator.generate_attendance_pdf(pc, sub, pd, pt, rolls, name) # pdf
                st.markdown(f"<p><b>Class:</b> {pc} | <b>Date:</b> {pd} | <b>Present:</b> {len(rolls)}</p>", unsafe_allow_html=True)
                st.download_button(f"Download PDF ({pc} - {pd})", pdf, f"{sub}_{pc}_{pd}.pdf", "application/pdf", key=f"dl_{pc}_{pd}_{pt}")
        return

    sec = logic.check_and_refresh_token()                 # countdown seconds
    present = csv_handler.read_present_students(state["class_name"], state["subject"], state["date"], state["lecture_time"])
    st.markdown(f"<h2>Live: {state['class_name']} — {state['subject']}</h2><p><b>Date:</b> {state['date']} ({state['lecture_time']})</p><h3>Present Students: {len(present)}</h3>", unsafe_allow_html=True)
    st.image(qr_code.generate_qr_image(f"{get_base_url()}/?token={state['token']}")) # live qr
    lbl = "Initial QR (20s):" if state.get("qr_count", 1) <= 1 else "QR refreshes in:"
    st.markdown(f"<p><b>{lbl} {sec}s</b></p>", unsafe_allow_html=True)

    if st.button("Stop Attendance"):
        logic.stop_session()                              # stop session
        st.rerun()
    pdf = pdf_generator.generate_attendance_pdf(state["class_name"], state["subject"], state["date"], state["lecture_time"], present, name)
    st.download_button("Download PDF Report", pdf, f"Attendance_{state['class_name']}_{state['subject']}_{state['date']}.pdf", "application/pdf")
    if present:
        st.markdown(f"<p><b>Present:</b> {', '.join([f'Roll {r}' for r in present])}</p>", unsafe_allow_html=True)
    time.sleep(1)                                         # wait 1 second
    st.rerun()                                            # rerun loop

def render_student_screen(token):
    state = logic.get_system_state()                      # fetch session state
    cid = state.get("session_id", f"{state['class_name']}_{state['subject']}_{state['date']}_{state['lecture_time']}")
    st.markdown("<h1>Student Attendance</h1><hr>", unsafe_allow_html=True)

    if st.session_state.get("submitted_session_id") == cid:
        st.markdown(f"<h3>Attendance Recorded</h3><p>Your attendance for <b>Roll No. {st.session_state.get('submitted_roll')}</b> has been recorded.</p>", unsafe_allow_html=True)
        return

    status = logic.verify_scanned_token(token)            # verify qr token
    if status == "SESSION_NOT_ACTIVE":
        st.markdown("<p><b>Attendance session is not currently active.</b></p>", unsafe_allow_html=True)
        return
    if status == "TOKEN_VALID":
        st.session_state.update(token_time=time.time(), valid_token=token) # cache valid token
    if st.session_state.get("valid_token") != token or (time.time() - st.session_state.get("token_time", 0)) > 60:
        st.markdown("<p><b>QR Code expired. Please scan the latest QR code.</b></p>", unsafe_allow_html=True)
        return

    st.markdown(f"<p><b>Class:</b> {state['class_name']} | <b>Subject:</b> {state['subject']}</p><p><b>Faculty:</b> {state.get('faculty_name', 'Ms. Seema Nagrani')}</p>", unsafe_allow_html=True)
    with st.form("student_form"):
        roll = st.text_input("Enter Roll Number:")        # roll number input
        if st.form_submit_button("Submit Attendance"):
            ip = (getattr(st.context, "headers", {}).get("x-forwarded-for") or "127.0.0.1").split(",")[0].strip()
            res = logic.process_attendance_submission(state["class_name"], state["subject"], state["date"], state["lecture_time"], roll.strip(), ip)
            if res == "EMPTY_ROLL_NUMBER":
                st.markdown("<p><b>Error:</b> Please enter your roll number.</p>", unsafe_allow_html=True)
            elif res == "ALREADY_MARKED":
                st.markdown(f"<p><b>Notice:</b> Roll {roll.strip()} is already marked for this lecture.</p>", unsafe_allow_html=True)
            elif res == "SUCCESS":
                st.session_state.update(submitted_session_id=cid, submitted_roll=roll.strip())
                st.rerun()


def render_app():
    st.set_page_config(page_title="Smart Attendance", page_icon="📋", layout="centered") # page config
    tok = st.query_params.get("token")                    # read query param
    render_student_screen(tok) if tok else render_teacher_screen() # router
