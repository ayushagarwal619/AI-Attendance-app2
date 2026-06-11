import re
import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card
from src.database.db import (
    check_teacher_exists, create_teacher, teacher_login,
    get_teacher_subjects, get_attendance_for_teacher,
    reset_teacher_password,
)
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog
from src.pipelines.face_pipeline import predict_attendance
from src.components.dialog_attendance_results import attendance_result_dialog
import numpy as np
from datetime import datetime
import pandas as pd
from src.database.config import supabase
from src.components.dialog_voice_attendance import voice_attendance_dialog


# ─── Shared Helpers ──────────────────────────────────────────────────────────

def _topbar(teacher_name: str):
    st.markdown(f"""
    <style>
    .sa-topbar {{
        display:flex; align-items:center; justify-content:space-between;
        padding:0.85rem 0; border-bottom:1px solid #E5E7EB; margin-bottom:1.75rem;
    }}
    .sa-topbar-brand {{ display:flex; align-items:center; gap:10px; }}
    .sa-topbar-brand span {{
        font-size:1rem; font-weight:800; color:#4F46E5;
        letter-spacing:-0.03em; font-family:'Inter',sans-serif;
    }}
    .sa-topbar-right {{ display:flex; align-items:center; gap:10px; }}
    .sa-avatar {{
        width:34px; height:34px; border-radius:50%;
        background:linear-gradient(135deg,#4F46E5,#7C3AED);
        color:#fff; font-size:0.85rem; font-weight:700;
        display:flex; align-items:center; justify-content:center;
        font-family:'Inter',sans-serif; flex-shrink:0;
    }}
    .sa-user-name {{
        font-size:0.85rem; font-weight:600; color:#111827;
        font-family:'Inter',sans-serif;
    }}
    .sa-user-role {{
        font-size:0.72rem; color:#6B7280; font-family:'Inter',sans-serif;
    }}
    </style>
    <div class="sa-topbar">
      <div class="sa-topbar-brand">
        <svg width="28" height="28" viewBox="0 0 32 32" fill="none">
          <rect width="32" height="32" rx="8" fill="#4F46E5"/>
          <path d="M8 10h10M8 16h16M8 22h12" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
          <circle cx="24" cy="10" r="3" fill="#06B6D4"/>
        </svg>
        <span>SmartAttend</span>
      </div>
      <div class="sa-topbar-right">
        <div class="sa-avatar">{teacher_name[:1].upper()}</div>
        <div>
          <div class="sa-user-name">{teacher_name}</div>
          <div class="sa-user-role">Teacher</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def _section_header(title, subtitle=""):
    st.markdown(f"""
    <div style="margin-bottom:1rem;">
      <h2 style="margin:0;font-size:1.15rem;font-weight:700;color:#111827;
                 font-family:'Inter',sans-serif;letter-spacing:-0.02em;">{title}</h2>
      {'<p style="margin:4px 0 0;font-size:0.82rem;color:#6B7280;font-family:Inter,sans-serif;">'+subtitle+'</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def _teacher_stats(total_subjects, total_students, total_sessions):
    st.markdown(f"""
    <style>
    .sa-t-stats {{
        display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin-bottom:1.75rem;
    }}
    .sa-t-stat {{
        background:#fff; border:1px solid #E5E7EB; border-radius:12px;
        padding:1.1rem 1.25rem; position:relative; overflow:hidden;
    }}
    .sa-t-stat::before {{
        content:''; position:absolute; bottom:0; left:0; right:0; height:3px;
    }}
    .sa-t-stat.s1::before {{ background:#4F46E5; }}
    .sa-t-stat.s2::before {{ background:#06B6D4; }}
    .sa-t-stat.s3::before {{ background:#7C3AED; }}
    .sa-t-lbl {{
        font-size:0.7rem; font-weight:600; text-transform:uppercase;
        letter-spacing:0.07em; color:#6B7280; font-family:'Inter',sans-serif; margin-bottom:6px;
    }}
    .sa-t-val {{
        font-size:1.6rem; font-weight:800; letter-spacing:-0.04em;
        font-family:'Inter',sans-serif; color:#111827; line-height:1;
    }}
    .sa-t-sub {{ font-size:0.72rem; color:#9CA3AF; font-family:'Inter',sans-serif; margin-top:4px; }}
    @media(max-width:768px) {{ .sa-t-stats {{ grid-template-columns:1fr 1fr; }} }}
    </style>
    <div class="sa-t-stats">
      <div class="sa-t-stat s1">
        <div class="sa-t-lbl">Subjects</div>
        <div class="sa-t-val">{total_subjects}</div>
        <div class="sa-t-sub">managed</div>
      </div>
      <div class="sa-t-stat s2">
        <div class="sa-t-lbl">Total Students</div>
        <div class="sa-t-val">{total_students}</div>
        <div class="sa-t-sub">enrolled across subjects</div>
      </div>
      <div class="sa-t-stat s3">
        <div class="sa-t-lbl">Attendance Sessions</div>
        <div class="sa-t-val">{total_sessions}</div>
        <div class="sa-t-sub">recorded</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ─── Tab pill component ───────────────────────────────────────────────────────
def _tab_pills():
    tabs = {
        "take_attendance":    ("📷", "Take Attendance"),
        "manage_subjects":    ("📚", "Subjects"),
        "attendance_records": ("📊", "Records"),
    }
    current = st.session_state.get("current_teacher_tab", "take_attendance")
    st.markdown("""
    <style>
    .sa-tab-row {{ display:flex; gap:6px; margin-bottom:1.5rem; }}
    </style>
    <div class="sa-tab-row">
    """, unsafe_allow_html=True)

    cols = st.columns(len(tabs))
    for col, (key, (icon, label)) in zip(cols, tabs.items()):
        btn_type = "primary" if current == key else "secondary"
        with col:
            if st.button(f"{icon}  {label}", type=btn_type, use_container_width=True, key=f"tab_{key}"):
                st.session_state.current_teacher_tab = key
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ─── Main Router ─────────────────────────────────────────────────────────────
def teacher_screen():
    style_background_dashboard()
    style_base_layout()

    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif st.session_state.get("teacher_login_type") == "register":
        teacher_screen_register()
    elif st.session_state.get("teacher_login_type") == "forgot_password":
        teacher_screen_forgot_password()
    else:
        teacher_screen_login()


# ─── Dashboard ───────────────────────────────────────────────────────────────
def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    teacher_name = teacher_data["name"]
    teacher_id   = teacher_data["teacher_id"]

    _topbar(teacher_name)

    # Action row
    a1, a2, a3, _ = st.columns([1, 1, 1, 3])
    with a1:
        if st.button("⇄ Switch to Student", type="secondary", use_container_width=True):
            st.session_state["login_type"] = "student"
            st.rerun()
    with a2:
        if st.button("Sign Out", type="secondary", use_container_width=True):
            st.session_state["is_logged_in"] = False
            del st.session_state.teacher_data
            st.rerun()

    st.markdown('<hr style="border:none;border-top:1px solid #E5E7EB;margin:0 0 1.5rem;">', unsafe_allow_html=True)

    # Stats
    all_subjects   = get_teacher_subjects(teacher_id)
    total_students = sum(s.get("total_students", 0) for s in all_subjects)
    total_sessions = sum(s.get("total_classes", 0)  for s in all_subjects)
    _teacher_stats(len(all_subjects), total_students, total_sessions)

    # Tab navigation
    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = "take_attendance"

    _tab_pills()
    st.markdown('<hr style="border:none;border-top:1px solid #E5E7EB;margin:0 0 1.5rem;">', unsafe_allow_html=True)

    tab = st.session_state.current_teacher_tab
    if tab == "take_attendance":
        teacher_tab_take_attendance()
    elif tab == "manage_subjects":
        teacher_tab_manage_subjects()
    elif tab == "attendance_records":
        teacher_tab_attendance_records()

    footer_dashboard()


# ─── Tab: Take Attendance ─────────────────────────────────────────────────────
def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data["teacher_id"]
    _section_header("Take AI Attendance", "Upload class photos or record audio to mark attendance automatically.")

    if "attendance_images" not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subjects(teacher_id)
    if not subjects:
        st.markdown("""
        <div style="background:#fff;border:1px solid #E5E7EB;border-radius:12px;
             padding:3rem 2rem;text-align:center;">
          <div style="font-size:2rem;margin-bottom:10px;">📭</div>
          <div style="font-size:0.9rem;font-weight:600;color:#374151;font-family:'Inter',sans-serif;">
            No subjects yet
          </div>
          <div style="font-size:0.8rem;color:#9CA3AF;font-family:'Inter',sans-serif;margin-top:4px;">
            Go to Subjects tab and create your first subject.
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    subject_options = {f"{s['name']}  ·  {s['subject_code']}": s["subject_id"] for s in subjects}

    col1, col2 = st.columns([3, 1], vertical_alignment="bottom")
    with col1:
        selected_label = st.selectbox("Select Subject", options=list(subject_options.keys()))
    with col2:
        if st.button("＋ Add Photos", type="primary", use_container_width=True, icon=":material/photo_prints:"):
            add_photos_dialog()

    selected_id = subject_options[selected_label]

    if st.session_state.attendance_images:
        st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
        _section_header(f"Photos ({len(st.session_state.attendance_images)})")
        gallery = st.columns(4)
        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery[idx % 4]:
                st.image(img, use_container_width=True, caption=f"Photo {idx+1}")

    st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
    has_photos = bool(st.session_state.attendance_images)
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("🗑  Clear Photos", type="secondary", use_container_width=True, disabled=not has_photos):
            st.session_state.attendance_images = []
            st.rerun()

    with c2:
        if st.button("🔍  Run Face Analysis", type="primary", use_container_width=True, disabled=not has_photos):
            with st.spinner("Scanning classroom photos with AI…"):
                all_detected_ids = {}
                for idx, img in enumerate(st.session_state.attendance_images):
                    img_np = np.array(img.convert("RGB"))
                    detected, _, _ = predict_attendance(img_np)
                    if detected:
                        for sid in detected.keys():
                            all_detected_ids.setdefault(int(sid), []).append(f"Photo {idx+1}")

                enrolled_res     = supabase.table("subject_students").select("*, students(*)").eq("subject_id", selected_id).execute()
                enrolled_students = enrolled_res.data

                if not enrolled_students:
                    st.warning("No students are enrolled in this subject.")
                else:
                    results, logs = [], []
                    ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                    for node in enrolled_students:
                        student  = node["students"]
                        sources  = all_detected_ids.get(int(student["student_id"]), [])
                        present  = len(sources) > 0
                        results.append({
                            "Name":   student["name"],
                            "ID":     student["student_id"],
                            "Source": ", ".join(sources) if present else "—",
                            "Status": "✅ Present" if present else "❌ Absent",
                        })
                        logs.append({
                            "student_id": student["student_id"],
                            "subject_id": selected_id,
                            "timestamp":  ts,
                            "is_present": bool(present),
                        })
                    attendance_result_dialog(pd.DataFrame(results), logs)

    with c3:
        if st.button("🎙  Voice Attendance", type="secondary", use_container_width=True):
            voice_attendance_dialog(selected_id)


# ─── Tab: Manage Subjects ─────────────────────────────────────────────────────
def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data["teacher_id"]

    h1, h2 = st.columns([3, 1], vertical_alignment="center")
    with h1:
        _section_header("Your Subjects", "Manage subjects and share join codes with students.")
    with h2:
        if st.button("＋ New Subject", type="primary", use_container_width=True):
            create_subject_dialog(teacher_id)

    subjects = get_teacher_subjects(teacher_id)
    if not subjects:
        st.markdown("""
        <div style="background:#fff;border:1px solid #E5E7EB;border-radius:12px;
             padding:3rem 2rem;text-align:center;">
          <div style="font-size:2rem;margin-bottom:10px;">📂</div>
          <div style="font-size:0.9rem;font-weight:600;color:#374151;font-family:'Inter',sans-serif;">
            No subjects yet
          </div>
          <div style="font-size:0.8rem;color:#9CA3AF;font-family:'Inter',sans-serif;margin-top:4px;">
            Click "+ New Subject" to get started.
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    cols = st.columns(2, gap="medium")
    for i, sub in enumerate(subjects):
        def _make_share(s):
            def share_btn():
                if st.button(
                    f"Share Join Code",
                    type="tertiary",
                    use_container_width=True,
                    icon=":material/share:",
                    key=f"share_{s['subject_code']}",
                ):
                    share_subject_dialog(s["name"], s["subject_code"])
                st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
            return share_btn

        with cols[i % 2]:
            subject_card(
                name=sub["name"],
                code=sub["subject_code"],
                section=sub["section"],
                stats=[
                    ("🎓", "Students", sub.get("total_students", 0)),
                    ("📅", "Sessions",  sub.get("total_classes", 0)),
                ],
                footer_callback=_make_share(sub),
            )


# ─── Tab: Attendance Records ──────────────────────────────────────────────────
def teacher_tab_attendance_records():
    _section_header("Attendance Records", "All past attendance sessions sorted by most recent.")
    teacher_id = st.session_state.teacher_data["teacher_id"]
    records    = get_attendance_for_teacher(teacher_id)

    if not records:
        st.markdown("""
        <div style="background:#fff;border:1px solid #E5E7EB;border-radius:12px;
             padding:3rem 2rem;text-align:center;">
          <div style="font-size:2rem;margin-bottom:10px;">📋</div>
          <div style="font-size:0.9rem;font-weight:600;color:#374151;font-family:'Inter',sans-serif;">
            No records yet
          </div>
          <div style="font-size:0.8rem;color:#9CA3AF;font-family:'Inter',sans-serif;margin-top:4px;">
            Take your first attendance session to see records here.
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    data = []
    for r in records:
        ts = r.get("timestamp")
        data.append({
            "ts_group":     ts.split(".")[0] if ts else None,
            "Time":         datetime.fromisoformat(ts).strftime("%d %b %Y  %I:%M %p") if ts else "N/A",
            "Subject":      r["subjects"]["name"],
            "Subject Code": r["subjects"]["subject_code"],
            "is_present":   bool(r.get("is_present", False)),
        })

    df = pd.DataFrame(data)
    summary = (
        df.groupby(["ts_group", "Time", "Subject", "Subject Code"])
        .agg(Present_Count=("is_present", "sum"), Total_Count=("is_present", "count"))
        .reset_index()
    )
    summary["Attendance"] = (
        "✅ " + summary["Present_Count"].astype(str)
        + " / " + summary["Total_Count"].astype(str) + " students"
    )
    display_df = (
        summary.sort_values("ts_group", ascending=False)
        [["Time", "Subject", "Subject Code", "Attendance"]]
    )
    st.dataframe(display_df, use_container_width=True, hide_index=True)


# ─── Login Helpers ────────────────────────────────────────────────────────────
def login_teacher(username, password):
    if not username or not password:
        return False
    teacher = teacher_login(username, password)
    if teacher:
        st.session_state.user_role   = "teacher"
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    return False


def register_teacher(username, name, mobile, password, password_confirm):
    if not username or not name or not password:
        return False, "All fields are required."
    if not mobile:
        return False, "Mobile number is required."
    if not re.match(r"^\+?[\d\s\-]{7,15}$", mobile):
        return False, "Enter a valid mobile number."
    if check_teacher_exists(username):
        return False, "Username already taken."
    if password != password_confirm:
        return False, "Passwords do not match."
    try:
        create_teacher(username, password, name, mobile)
        return True, "Account created! You can now log in."
    except Exception as e:
        return False, f"Error: {e}"


# ─── Auth Layout Helper ───────────────────────────────────────────────────────
def _auth_shell(title: str, subtitle: str, back_label: str, back_action):
    """Renders a centred auth card; returns nothing — caller fills in content."""
    st.markdown("""
    <style>
    .sa-auth-wrap { max-width:460px; margin:2.5rem auto 0; }
    .sa-auth-logo-row {
        display:flex; align-items:center; justify-content:center;
        gap:10px; margin-bottom:1.25rem;
    }
    .sa-auth-logo-row span {
        font-size:1rem; font-weight:800; color:#4F46E5;
        font-family:'Inter',sans-serif; letter-spacing:-0.03em;
    }
    .sa-auth-title {
        text-align:center; margin-bottom:0.4rem;
        font-size:1.35rem; font-weight:800; color:#111827;
        font-family:'Inter',sans-serif; letter-spacing:-0.03em;
    }
    .sa-auth-sub {
        text-align:center; margin-bottom:1.75rem;
        font-size:0.85rem; color:#6B7280; font-family:'Inter',sans-serif;
    }
    .sa-auth-card {
        background:#fff; border:1px solid #E5E7EB;
        border-radius:16px; padding:2rem;
    }
    </style>
    """, unsafe_allow_html=True)

    back_col, _ = st.columns([1, 3])
    with back_col:
        if st.button(f"← {back_label}", type="secondary"):
            back_action()
            st.rerun()

    st.markdown(f"""
    <div class="sa-auth-logo-row">
      <svg width="26" height="26" viewBox="0 0 32 32" fill="none">
        <rect width="32" height="32" rx="8" fill="#4F46E5"/>
        <path d="M8 10h10M8 16h16M8 22h12" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
        <circle cx="24" cy="10" r="3" fill="#06B6D4"/>
      </svg>
      <span>SmartAttend</span>
    </div>
    <div class="sa-auth-title">{title}</div>
    <div class="sa-auth-sub">{subtitle}</div>
    <div class="sa-auth-card">
    """, unsafe_allow_html=True)


# ─── Login Screen ─────────────────────────────────────────────────────────────
def teacher_screen_login():
    def go_home():
        st.session_state["login_type"] = None

    _auth_shell(
        "Teacher Login",
        "Sign in to your SmartAttend account",
        "Home", go_home,
    )

    username = st.text_input("Username", placeholder="e.g. ananya_roy")
    password = st.text_input("Password", type="password", placeholder="Your password")

    st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)

    col_login, col_reg = st.columns(2)
    with col_login:
        if st.button("Sign In", type="primary", use_container_width=True):
            if login_teacher(username, password):
                st.toast("Welcome back! 👋")
                import time; time.sleep(0.8)
                st.rerun()
            else:
                st.error("Incorrect username or password.")
    with col_reg:
        if st.button("Create Account", type="secondary", use_container_width=True):
            st.session_state.teacher_login_type = "register"
            st.rerun()

    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
    fp_col, _ = st.columns([1, 2])
    with fp_col:
        if st.button("Forgot password?", type="tertiary"):
            st.session_state.teacher_login_type = "forgot_password"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    footer_dashboard()


# ─── Register Screen ──────────────────────────────────────────────────────────
def teacher_screen_register():
    def go_login():
        st.session_state.teacher_login_type = "login"

    _auth_shell(
        "Create Teacher Account",
        "Set up your SmartAttend profile",
        "Back to Login", go_login,
    )

    c1, c2 = st.columns(2)
    with c1:
        username = st.text_input("Username", placeholder="ananya_roy")
    with c2:
        name = st.text_input("Full Name", placeholder="Ananya Roy")

    mobile   = st.text_input("Mobile Number", placeholder="+91 9876543210")
    password = st.text_input("Password", type="password", placeholder="Min. 6 characters")
    password_confirm = st.text_input("Confirm Password", type="password", placeholder="Repeat password")

    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    if st.button("Create Account", type="primary", use_container_width=True):
        ok, msg = register_teacher(username, name, mobile, password, password_confirm)
        if ok:
            st.success(msg)
            import time; time.sleep(1.5)
            st.session_state.teacher_login_type = "login"
            st.rerun()
        else:
            st.error(msg)

    st.markdown("</div>", unsafe_allow_html=True)
    footer_dashboard()


# ─── Forgot Password Screen ───────────────────────────────────────────────────
def teacher_screen_forgot_password():
    def go_login():
        st.session_state.teacher_login_type = "login"
        for k in ["forgot_step", "fp_otp", "fp_mobile_entered", "fp_otp_time"]:
            st.session_state.pop(k, None)

    _auth_shell(
        "Reset Password",
        "We'll send an OTP to your registered mobile number",
        "Back to Login", go_login,
    )

    if "forgot_step" not in st.session_state:
        st.session_state.forgot_step = "enter_mobile"

    step = st.session_state.forgot_step

    # Step indicators
    steps = ["Enter Mobile", "Verify OTP", "New Password"]
    step_keys = ["enter_mobile", "verify_otp", "reset_password"]
    current_idx = step_keys.index(step) if step in step_keys else 0
    indicator_html = '<div style="display:flex;gap:6px;margin-bottom:1.25rem;">'
    for idx, s in enumerate(steps):
        active = idx == current_idx
        done   = idx < current_idx
        color  = "#4F46E5" if active else ("#10B981" if done else "#E5E7EB")
        tc     = "#fff" if (active or done) else "#9CA3AF"
        indicator_html += f"""
        <div style="flex:1;background:{color};color:{tc};border-radius:6px;padding:6px 8px;
             text-align:center;font-size:0.72rem;font-weight:600;font-family:'Inter',sans-serif;">
          {'✓ ' if done else ''}{s}
        </div>"""
    indicator_html += "</div>"
    st.markdown(indicator_html, unsafe_allow_html=True)

    if step == "enter_mobile":
        mobile = st.text_input("Registered Mobile Number", placeholder="+91 9876543210", key="fp_mobile")
        if st.button("Send OTP", type="primary", use_container_width=True):
            if mobile:
                import random, time as _t
                # ── SMS ABSTRACTION LAYER ──────────────────────────────────────
                # Plug in Twilio / MSG91 / Fast2SMS here:
                #   from src.database.sms_service import send_otp
                #   send_otp(mobile, otp)
                # ─────────────────────────────────────────────────────────────
                otp = str(random.randint(100000, 999999))
                st.session_state.fp_otp             = otp
                st.session_state.fp_mobile_entered  = mobile
                st.session_state.fp_otp_time        = _t.time()
                st.info(f"OTP sent! (Dev mode — OTP: **{otp}**)")
                st.session_state.forgot_step = "verify_otp"
                st.rerun()
            else:
                st.warning("Please enter your mobile number.")

    elif step == "verify_otp":
        st.markdown(f'<p style="font-family:Inter,sans-serif;font-size:0.82rem;color:#4B5563;">OTP sent to {st.session_state.get("fp_mobile_entered","")}</p>', unsafe_allow_html=True)
        otp_in = st.text_input("Enter 6-digit OTP", max_chars=6, key="fp_otp_input")
        col_v, col_r = st.columns(2)
        with col_v:
            if st.button("Verify OTP", type="primary", use_container_width=True):
                import time as _t
                elapsed = _t.time() - st.session_state.get("fp_otp_time", 0)
                if elapsed > 300:
                    st.error("OTP expired. Please request a new one.")
                    st.session_state.forgot_step = "enter_mobile"
                elif otp_in == st.session_state.get("fp_otp"):
                    st.session_state.forgot_step = "reset_password"
                    st.rerun()
                else:
                    st.error("Incorrect OTP.")
        with col_r:
            if st.button("Resend OTP", type="secondary", use_container_width=True):
                st.session_state.forgot_step = "enter_mobile"
                st.rerun()

    elif step == "reset_password":
        st.success("Identity verified. Set your new password.")
        new_pass     = st.text_input("New Password", type="password", key="fp_new")
        confirm_pass = st.text_input("Confirm Password", type="password", key="fp_confirm")
        if st.button("Update Password", type="primary", use_container_width=True):
            if not new_pass or not confirm_pass:
                st.warning("Fill in both fields.")
            elif new_pass != confirm_pass:
                st.error("Passwords do not match.")
            elif len(new_pass) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                ok = reset_teacher_password(st.session_state.get("fp_mobile_entered"), new_pass)
                if ok:
                    st.success("Password updated! Redirecting to login…")
                    for k in ["forgot_step", "fp_otp", "fp_mobile_entered", "fp_otp_time"]:
                        st.session_state.pop(k, None)
                    import time as _t; _t.sleep(1.2)
                    st.session_state.teacher_login_type = "login"
                    st.rerun()
                else:
                    st.error("No account found with that mobile number.")

    st.markdown("</div>", unsafe_allow_html=True)
    footer_dashboard()
