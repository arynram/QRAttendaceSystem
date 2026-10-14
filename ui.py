import time                                               # time module for countdown and refresh
from datetime import datetime                             # for date and time calculations
import streamlit as st                                    # streamlit web framework
import logic                                              # attendance business logic
import qr_code                                            # qr generation and ip utilities
import csv_handler                                        # csv database handler
import pdf_generator                                      # pdf report generator


# ─────────────────────────────────────────────────────────────────────────────
# NETWORK & IP UTILITIES
# ─────────────────────────────────────────────────────────────────────────────
def get_client_ip():
    headers = getattr(st.context, "headers", {})
    xff = headers.get("x-forwarded-for") or headers.get("X-Forwarded-For")
    if xff:
        return xff.split(",")[0].strip()
    cf_ip = headers.get("cf-connecting-ip") or headers.get("CF-Connecting-IP")
    if cf_ip:
        return cf_ip.strip()
    ctx_ip = getattr(st.context, "ip_address", None)
    if ctx_ip:
        return str(ctx_ip).strip()
    return None


def get_base_url(server_ip, server_port="8501"):
    headers = getattr(st.context, "headers", {})
    host = headers.get("host") or headers.get("Host")
    if host and "localhost" not in host and "127.0.0.1" not in host:
        proto = headers.get("x-forwarded-proto", "https" if "streamlit.app" in host else "http")
        return f"{proto}://{host}"
    return f"http://{server_ip}:{server_port}"


# ─────────────────────────────────────────────────────────────────────────────
# MINIMALIST DARK THEME CSS
# ─────────────────────────────────────────────────────────────────────────────
def inject_minimal_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #09090b !important;
        color: #f4f4f5 !important;
    }

    .stApp {
        background-color: #09090b !important;
        max-width: 100vw;
    }

    /* Minimal Card */
    .min-card {
        background: #121217;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 16px;
    }

    /* PIN Preview Box */
    .pin-display {
        font-family: 'JetBrains Mono', monospace;
        font-size: 32px;
        font-weight: 700;
        letter-spacing: 12px;
        color: #38bdf8;
        background: #18181b;
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 14px;
        padding: 14px 20px;
        text-align: center;
        min-height: 64px;
        margin: 12px 0 20px 0;
    }

    /* Smart Board Large Touch Buttons */
    .stButton > button {
        border-radius: 12px !important;
        font-family: 'JetBrains Mono', 'Inter', monospace !important;
        font-size: 20px !important;
        font-weight: 600 !important;
        min-height: 56px !important;
        background: #18181b !important;
        color: #f4f4f5 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        transition: all 0.15s ease !important;
    }

    .stButton > button:hover {
        background: #27272a !important;
        border-color: rgba(255, 255, 255, 0.25) !important;
        color: #ffffff !important;
        transform: translateY(-1px);
    }

    .stButton > button[kind="primary"] {
        background: #2563eb !important;
        color: #ffffff !important;
        border: none !important;
        font-size: 16px !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: #1d4ed8 !important;
    }

    .stButton > button[kind="secondary"] {
        background: #7f1d1d !important;
        color: #fca5a5 !important;
        border: 1px solid #991b1b !important;
        font-size: 16px !important;
    }

    /* Download Buttons */
    .stDownloadButton > button {
        border-radius: 12px !important;
        min-height: 44px !important;
        background: #18181b !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #38bdf8 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }

    .stDownloadButton > button:hover {
        background: #27272a !important;
        border-color: #38bdf8 !important;
    }

    /* Segment Pills */
    div[role="radiogroup"] {
        gap: 8px !important;
    }

    div[role="radiogroup"] > label {
        background: #18181b !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        padding: 8px 16px !important;
        color: #e4e4e7 !important;
        font-weight: 500 !important;
    }

    /* Date and Text Input Styling */
    .stTextInput > div > div > input,
    .stDateInput > div > div > input {
        background: #18181b !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
        color: #f4f4f5 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 15px !important;
        padding: 10px 14px !important;
    }

    .stDateInput label, .stTextInput label {
        font-size: 11px !important;
        font-weight: 600 !important;
        color: #a1a1aa !important;
        letter-spacing: 0.6px !important;
        text-transform: uppercase !important;
        margin-bottom: 4px !important;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 8px 18px;
        font-weight: 600;
        background: #121217;
        border: 1px solid rgba(255,255,255,0.08);
        color: #a1a1aa;
    }
    .stTabs [aria-selected="true"] {
        background: #2563eb !important;
        color: #ffffff !important;
        border-color: #2563eb !important;
    }

    /* Hide Default Chrome */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1.5rem !important; max-width: 860px !important; }
    </style>
    """, unsafe_allow_html=True)                           # apply minimal styles


# ─────────────────────────────────────────────────────────────────────────────
# SMART BOARD TOUCH PIN KEYPAD
# ─────────────────────────────────────────────────────────────────────────────
def render_smartboard_pin_screen():
    if "entered_pin" not in st.session_state:              # track entered PIN
        st.session_state["entered_pin"] = ""              # initialize empty
    if "pin_error" not in st.session_state:                # error state
        st.session_state["pin_error"] = ""                # initialize empty

    st.markdown("""
    <div style="text-align: center; margin-top: 24px; margin-bottom: 12px;">
        <div style="font-size: 13px; font-weight: 600; letter-spacing: 1.5px; color: #a1a1aa; text-transform: uppercase;">
            Faculty Smart Board Portal
        </div>
        <div style="font-size: 24px; font-weight: 700; color: #ffffff; margin-top: 4px;">
            Enter 6-Digit Faculty Code
        </div>
    </div>
    """, unsafe_allow_html=True)                          # title

    # Render PIN display dots / numbers
    entered = st.session_state["entered_pin"]
    masked = "".join(["● " for _ in entered]) + "".join(["_ " for _ in range(6 - len(entered))])
    display_content = masked.strip() if masked else "_ _ _ _ _ _"

    st.markdown(f"""
    <div class="pin-display">
        {display_content}
    </div>
    """, unsafe_allow_html=True)                          # preview PIN input

    if st.session_state["pin_error"]:                      # display error if invalid
        st.error(st.session_state["pin_error"])

    # 3x4 Touch Numeric Keypad
    keypad = [
        ["1", "2", "3"],
        ["4", "5", "6"],
        ["7", "8", "9"],
        ["⌫", "0", "UNLOCK"]
    ]

    for row in keypad:
        cols = st.columns(3)
        for i, key in enumerate(row):
            with cols[i]:
                if key == "UNLOCK":
                    if st.button("UNLOCK ⏎", key="btn_unlock", type="primary", use_container_width=True):
                        prof = logic.verify_teacher_pin(st.session_state["entered_pin"])
                        if prof:
                            st.session_state["smartboard_unlocked"] = True
                            st.session_state["teacher_profile"] = prof
                            st.session_state["pin_error"] = ""
                            st.rerun()
                        else:
                            st.session_state["pin_error"] = "Invalid faculty code. Please try again."
                            st.rerun()
                elif key == "⌫":
                    if st.button("⌫", key="btn_back", use_container_width=True):
                        st.session_state["entered_pin"] = st.session_state["entered_pin"][:-1]
                        st.session_state["pin_error"] = ""
                        st.rerun()
                else:
                    if st.button(key, key=f"btn_{key}", use_container_width=True):
                        if len(st.session_state["entered_pin"]) < 6:
                            st.session_state["entered_pin"] += key
                            st.session_state["pin_error"] = ""
                            st.rerun()

    # Clear input shortcut
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    if st.button("Clear Input", use_container_width=True):
        st.session_state["entered_pin"] = ""
        st.session_state["pin_error"] = ""
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# TEACHER PROFILE & ATTENDANCE DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
def render_teacher_screen():
    state = logic.get_system_state()                      # fetch shared state

    # If session NOT active and smartboard is locked -> prompt for PIN 123456
    if not state["active"] and not st.session_state.get("smartboard_unlocked", False):
        render_smartboard_pin_screen()
        return

    profile = st.session_state.get("teacher_profile", logic.TEACHER_PROFILES["123456"])
    faculty_name = profile.get("name", "Prof. Deepthi Rapeti")
    faculty_sub = profile.get("subject", "COOS")
    faculty_classes = profile.get("classes", ["AIML A", "AIML B", "AIML C", "AIML D"])

    # Auto network settings & time (IST)
    server_ip = qr_code.get_laptop_ip()
    server_port = "8501"
    ist_now = logic.get_ist_now()
    today_date = ist_now.strftime("%Y-%m-%d")
    auto_start, auto_end = logic.get_default_time_slot()
    auto_slot = f"{auto_start} - {auto_end}"

    # Profile Header
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown(f"""
        <div style="margin-bottom: 12px;">
            <div style="font-size: 22px; font-weight: 700; color: #ffffff;">{faculty_name}</div>
            <div style="font-size: 13px; color: #38bdf8; font-weight: 600;">
                Subject: {faculty_sub} • Department: AIML
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_h2:
        if not state["active"]:
            if st.button("🔒 Logout", use_container_width=True):
                st.session_state["smartboard_unlocked"] = False
                st.session_state["entered_pin"] = ""
                st.rerun()

    # ── CASE 1: SESSION NOT ACTIVE (NEW LECTURE & PAST RECORDS TABS) ─────────
    if not state["active"]:
        tab_start, tab_past = st.tabs(["⚡ Start Attendance", "📁 Past Attendance Records"])

        with tab_start:
            # 1. Class Selection
            st.markdown("<div style='font-size: 13px; color: #a1a1aa; font-weight: 600; margin-top: 10px; margin-bottom: 6px;'>SELECT CLASS</div>", unsafe_allow_html=True)
            class_choice = st.radio(
                "Select Class",
                faculty_classes,
                horizontal=True,
                label_visibility="collapsed"
            )

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

            # 2. Subject (Fixed to COOS for Prof. Deepthi Rapeti)
            st.markdown("<div style='font-size: 13px; color: #a1a1aa; font-weight: 600; margin-bottom: 6px;'>SUBJECT</div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="min-card" style="padding: 12px 18px; display: inline-block; border-color: rgba(56, 189, 248, 0.4); background: #18181b;">
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 15px; font-weight: 700; color: #38bdf8;">
                    {faculty_sub}
                </span>
                <span style="font-size: 12px; color: #71717a; margin-left: 8px;">(Computer Organization and Operating Systems)</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

            # 3. Editable Date and Time Slot Inputs
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                sel_date = st.date_input("📅 Lecture Date", value=ist_now.date())
                sel_date_str = sel_date.strftime("%Y-%m-%d")
            with col_d2:
                # Dynamic time slot: updates to live auto slot or user selection
                chosen_slot = st.session_state.get("chosen_slot", auto_slot)
                st.markdown(f"<div style='font-size:11px; font-weight:600; color:#a1a1aa; text-transform:uppercase; margin-bottom:4px;'>⏰ Lecture Time Slot (Live Auto: {auto_slot})</div>", unsafe_allow_html=True)
                sel_slot = st.text_input("Lecture Time Slot", value=chosen_slot, label_visibility="collapsed")

            # Quick Presets for Smart Board 1-Touch Selection
            col_p1, col_p2 = st.columns(2)
            alt_h = ist_now.hour % 24
            alt_slot = f"{ist_now.replace(hour=alt_h, minute=0).strftime('%I:%M %p')} - {ist_now.replace(hour=(alt_h+1)%24, minute=0).strftime('%I:%M %p')}"
            with col_p1:
                if st.button(f"⚡ Set Auto: {auto_slot}", use_container_width=True):
                    st.session_state["chosen_slot"] = auto_slot
                    st.rerun()
            with col_p2:
                if st.button(f"🕒 Set Hour: {alt_slot}", use_container_width=True):
                    st.session_state["chosen_slot"] = alt_slot
                    st.rerun()

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

            # Start Attendance Button
            if st.button("🚀 START ATTENDANCE SESSION", type="primary", use_container_width=True):
                logic.start_session(class_choice, faculty_sub, sel_date_str, sel_slot, "Round Robin", 2, faculty_name)
                st.rerun()

        with tab_past:
            # Past Attendance for Prof. Deepthi Rapeti's COOS Lectures
            past_sessions = csv_handler.get_subject_sessions(faculty_sub)

            if past_sessions:
                st.markdown("<div style='font-size: 14px; color: #a1a1aa; margin-top: 10px; margin-bottom: 14px;'>Download past attendance reports for COOS:</div>", unsafe_allow_html=True)
                for (c, d, t), rolls in sorted(past_sessions.items(), reverse=True):
                    with st.container():
                        st.markdown(f"""
                        <div class="min-card" style="display: flex; justify-content: space-between; align-items: center; padding: 14px 20px; margin-bottom: 8px;">
                            <div>
                                <span style="font-weight: 700; font-size: 16px; color: #ffffff;">{c}</span>
                                <span style="font-size: 13px; color: #71717a; margin-left: 10px;">📅 {d} &nbsp;|&nbsp; ⏰ {t}</span>
                            </div>
                            <div>
                                <span style="font-family: 'JetBrains Mono', monospace; font-size: 15px; font-weight: 700; color: #4ade80;">{len(rolls)}</span>
                                <span style="font-size: 12px; color: #a1a1aa;"> Present</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        pdf_data = pdf_generator.generate_attendance_pdf(c, faculty_sub, d, t, rolls, "Round Robin", faculty_name)
                        st.download_button(
                            label=f"📥 Download {c} Report ({d})",
                            data=pdf_data,
                            file_name=f"COOS_{c}_{d}.pdf",
                            mime="application/pdf",
                            key=f"dl_{c}_{d}_{t}",
                            use_container_width=True
                        )
                        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="min-card" style="text-align: center; padding: 30px; color: #71717a;">
                    No past COOS attendance sessions recorded yet. Start your first session above!
                </div>
                """, unsafe_allow_html=True)
        return

    # ── CASE 2: SESSION ACTIVE (DYNAMIC QR CODE) ─────────────────────────────
    seconds_left = logic.check_and_refresh_token()
    base_url = get_base_url(server_ip, server_port)
    qr_url = f"{base_url}/?token={state['token']}"
    qr_bytes = qr_code.generate_qr_image(qr_url)

    active_class = state["class_name"]
    active_sub = state["subject"]
    active_date = state["date"]
    active_slot = state["lecture_time"]
    present = csv_handler.read_present_students(active_class, active_sub, active_date, active_slot)

    # Active Bar
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
        <div>
            <span style="font-size: 22px; font-weight: 700; color: #ffffff;">{active_class} • {active_sub}</span>
            <div style="font-size: 12px; color: #71717a;">Faculty: {faculty_name} | {active_date} | {active_slot}</div>
        </div>
        <div style="text-align: right;">
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 28px; font-weight: 700; color: #38bdf8;">{len(present)}</span>
            <span style="font-size: 13px; color: #a1a1aa;"> Marked</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # QR Code centered
    col_l, col_qr, col_r = st.columns([1, 2.5, 1])
    with col_qr:
        st.image(qr_bytes, use_container_width=True)
        countdown_label = "Initial QR Code:" if seconds_left > 10 else "Token refreshes in:"
        st.markdown(f"""
        <div style="text-align: center; font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #71717a; margin-top: 6px;">
            {countdown_label} <span style="color: #38bdf8; font-weight: 700;">{seconds_left}s</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Stop & Download
    col_stop, col_pdf = st.columns(2)
    with col_stop:
        if st.button("🛑 STOP ATTENDANCE", type="secondary", use_container_width=True):
            logic.stop_session()
            st.rerun()
    with col_pdf:
        pdf_data = pdf_generator.generate_attendance_pdf(active_class, active_sub, active_date, active_slot, present, "Round Robin", faculty_name)
        st.download_button(
            label="📄 DOWNLOAD PDF REPORT",
            data=pdf_data,
            file_name=f"Attendance_{active_class}_{active_sub}_{active_date}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    # Live Present Rolls
    if present:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        rolls_html = "".join([f"<span style='background:#18181b; border:1px solid rgba(255,255,255,0.1); border-radius:8px; padding:4px 10px; font-family:JetBrains Mono,monospace; font-size:12px; color:#4ade80;'>Roll {r} ✓</span> " for r in present])
        st.markdown(f"<div style='display:flex; flex-wrap:wrap; gap:6px;'>{rolls_html}</div>", unsafe_allow_html=True)

    time.sleep(1)
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# STUDENT MOBILE ATTENDANCE SCREEN
# ─────────────────────────────────────────────────────────────────────────────
def render_student_screen(scanned_token):
    client_ip = get_client_ip()

    # -------------------------------------------------------------------------
    # [TEACHER DEMO: INDIA IP & VPN DETECTION]
    # Uncomment block below to block VPN and foreign IPs:
    # -------------------------------------------------------------------------
    # import ip_security
    # if "student_ip_checked" not in st.session_state:
    #     st.session_state["student_ip_checked"] = ip_security.check_ip_india_no_vpn(client_ip)
    # ip_result = st.session_state.get("student_ip_checked", {"allowed": True})
    # if not ip_result.get("allowed", True):
    #     st.error("Access Blocked: VPN detected or outside regional network.")
    #     return

    state = logic.get_system_state()
    current_session_id = state.get("session_id", f"{state['class_name']}_{state['subject']}_{state['date']}_{state['lecture_time']}")

    # -------------------------------------------------------------------------
    # [TEACHER DEMO: 1 IP = 1 ATTENDANCE DEVICE LOCK]
    # Uncomment block below to enforce 1 submission per phone / IP:
    # -------------------------------------------------------------------------
    # import ip_security
    # if ip_security.is_ip_already_used(state, client_ip):
    #     prev_roll = state.get("marked_ips", {}).get(client_ip, "Unknown")
    #     st.markdown(f"""
    #     <div class="min-card" style="text-align: center; margin-top: 40px; border-color: #22c55e;">
    #         <div style="font-size: 36px; margin-bottom: 8px;">✅</div>
    #         <div style="font-size: 20px; font-weight: 700; color: #ffffff;">Attendance Already Recorded</div>
    #         <div style="font-size: 24px; font-family: 'JetBrains Mono', monospace; color: #4ade80; margin: 10px 0;">Roll {prev_roll}</div>
    #         <div style="font-size: 13px; color: #a1a1aa;">This device / IP address has already marked attendance for this lecture.</div>
    #     </div>
    #     """, unsafe_allow_html=True)
    #     return

    # 2. Browser session check
    if st.session_state.get("submitted_session_id") == current_session_id and "submitted_roll" in st.session_state:
        already_roll = st.session_state["submitted_roll"]
        st.markdown(f"""
        <div class="min-card" style="text-align: center; margin-top: 40px; border-color: #22c55e;">
            <div style="font-size: 36px; margin-bottom: 8px;">✅</div>
            <div style="font-size: 20px; font-weight: 700; color: #ffffff;">Attendance Recorded</div>
            <div style="font-size: 24px; font-family: 'JetBrains Mono', monospace; color: #4ade80; margin: 10px 0;">Roll {already_roll}</div>
            <div style="font-size: 12px; color: #71717a;">Your attendance for this lecture has been recorded.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Verify Token
    token_status = logic.verify_scanned_token(scanned_token)

    if token_status == "SESSION_NOT_ACTIVE":
        st.warning("Attendance session is not currently active.")
        return

    now = time.time()
    if token_status == "TOKEN_VALID":
        st.session_state["token_time"] = now
        st.session_state["valid_token"] = scanned_token

    # 60s typing grace window
    is_valid = (
        st.session_state.get("valid_token") == scanned_token
        and (now - st.session_state.get("token_time", 0)) <= 60
    )

    if not is_valid:
        st.error("QR Code expired. Please scan the current code from the screen.")
        return

    class_name = state["class_name"]
    subject = state["subject"]
    date_str = state["date"]
    time_slot = state["lecture_time"]
    faculty = state.get("faculty_name", "Prof. Deepthi Rapeti")

    st.markdown(f"""
    <div style="text-align: center; margin-top: 20px; margin-bottom: 16px;">
        <div style="font-size: 20px; font-weight: 700; color: #ffffff;">{class_name} • {subject}</div>
        <div style="font-size: 13px; color: #38bdf8; margin-top: 2px;">Faculty: {faculty}</div>
        <div style="font-size: 12px; color: #71717a; margin-top: 2px;">{date_str} | {time_slot}</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("student_form"):
        roll_no = st.text_input("Enter Roll Number", placeholder="e.g. 39")
        submit = st.form_submit_button("MARK ATTENDANCE", type="primary", use_container_width=True)

        if submit:
            clean_roll = roll_no.strip()
            res, _ = logic.process_attendance_submission(class_name, subject, date_str, time_slot, clean_roll, client_ip)

            if res == "EMPTY_ROLL_NUMBER":
                st.warning("Please enter your roll number.")
            # elif res.startswith("IP_ALREADY_USED"):
            #     prev = res.split(":")[-1]
            #     st.error(f"This device/IP has already marked attendance for Roll No. {prev}.")
            elif res == "ALREADY_MARKED":
                st.warning(f"Roll No. {clean_roll} is already marked for this lecture.")
            elif res == "SUCCESS":
                st.session_state["submitted_session_id"] = current_session_id
                st.session_state["submitted_roll"] = clean_roll
                st.success(f"Roll No. {clean_roll} marked successfully!")
                time.sleep(0.8)
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
def render_app():
    st.set_page_config(
        page_title="Smart Attendance",
        page_icon="⚡",
        layout="centered"
    )
    inject_minimal_theme()

    token = st.query_params.get("token")
    if token:
        render_student_screen(token)
    else:
        render_teacher_screen()
