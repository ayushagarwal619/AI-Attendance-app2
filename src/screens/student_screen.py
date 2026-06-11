import streamlit as st
from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.footer import footer_dashboard
from PIL import Image
import numpy as np
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import (
    get_all_students, create_student,
    get_student_subjects, get_student_attendance,
    unenroll_student_to_subject,
)
import time
from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card


# ─── Top Navbar ──────────────────────────────────────────────────────────────
def _render_navbar(student_name: str):
    st.markdown(f"""
    <style>
    .sa-topbar {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.85rem 0;
        border-bottom: 1px solid #E5E7EB;
        margin-bottom: 1.75rem;
    }}
    .sa-topbar-brand {{
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    .sa-topbar-brand svg {{ flex-shrink: 0; }}
    .sa-topbar-brand span {{
        font-size: 1rem;
        font-weight: 800;
        color: #4F46E5;
        letter-spacing: -0.03em;
        font-family: 'Inter', sans-serif;
    }}
    .sa-topbar-right {{
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    .sa-avatar {{
        width: 34px;
        height: 34px;
        border-radius: 50%;
        background: linear-gradient(135deg,#4F46E5,#7C3AED);
        color: #fff;
        font-size: 0.85rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Inter', sans-serif;
        flex-shrink: 0;
    }}
    .sa-user-info span {{
        display: block;
        font-family: 'Inter', sans-serif;
    }}
    .sa-user-info .name {{
        font-size: 0.85rem;
        font-weight: 600;
        color: #111827;
    }}
    .sa-user-info .role {{
        font-size: 0.72rem;
        color: #6B7280;
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
        <div class="sa-avatar">{student_name[:1].upper()}</div>
        <div class="sa-user-info">
          <span class="name">{student_name}</span>
          <span class="role">Student</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ─── Stats Row ────────────────────────────────────────────────────────────────
def _render_stats(n_subjects, total, attended, pct):
    color = "#10B981" if pct >= 75 else ("#F59E0B" if pct >= 50 else "#EF4444")
    st.markdown(f"""
    <style>
    .sa-stats-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 14px;
        margin-bottom: 1.75rem;
    }}
    .sa-stat-card {{
        background: #fff;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 1.1rem 1.25rem;
        position: relative;
        overflow: hidden;
    }}
    .sa-stat-card::before {{
        content: '';
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 3px;
    }}
    .sa-stat-card.primary::before {{ background: #4F46E5; }}
    .sa-stat-card.success::before {{ background: {color}; }}
    .sa-stat-card.accent::before  {{ background: #06B6D4; }}
    .sa-stat-card.purple::before  {{ background: #7C3AED; }}
    .sa-stat-lbl {{
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #6B7280;
        font-family: 'Inter', sans-serif;
        margin-bottom: 6px;
    }}
    .sa-stat-val {{
        font-size: 1.6rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        font-family: 'Inter', sans-serif;
        color: #111827;
        line-height: 1;
    }}
    .sa-stat-sub {{
        font-size: 0.72rem;
        color: #9CA3AF;
        font-family: 'Inter', sans-serif;
        margin-top: 4px;
    }}
    @media(max-width:768px) {{
        .sa-stats-grid {{ grid-template-columns: repeat(2,1fr); }}
    }}
    </style>
    <div class="sa-stats-grid">
      <div class="sa-stat-card primary">
        <div class="sa-stat-lbl">Subjects</div>
        <div class="sa-stat-val">{n_subjects}</div>
        <div class="sa-stat-sub">enrolled</div>
      </div>
      <div class="sa-stat-card accent">
        <div class="sa-stat-lbl">Total Classes</div>
        <div class="sa-stat-val">{total}</div>
        <div class="sa-stat-sub">scheduled</div>
      </div>
      <div class="sa-stat-card purple">
        <div class="sa-stat-lbl">Attended</div>
        <div class="sa-stat-val">{attended}</div>
        <div class="sa-stat-sub">classes present</div>
      </div>
      <div class="sa-stat-card success">
        <div class="sa-stat-lbl">Overall Attendance</div>
        <div class="sa-stat-val" style="color:{color};">{pct}%</div>
        <div class="sa-stat-sub">{'On track ✓' if pct >= 75 else 'Needs improvement ⚠'}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ─── Section Header ───────────────────────────────────────────────────────────
def _section_header(title: str, subtitle: str = ""):
    st.markdown(f"""
    <div style="margin-bottom:1rem;">
      <h2 style="margin:0; font-size:1.15rem; font-weight:700; color:#111827;
                 font-family:'Inter',sans-serif; letter-spacing:-0.02em;">{title}</h2>
      {'<p style="margin:4px 0 0; font-size:0.82rem; color:#6B7280; font-family:Inter,sans-serif;">'+subtitle+'</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


# ─── Dashboard ────────────────────────────────────────────────────────────────
def student_dashboard():
    student_data = st.session_state.student_data
    student_id   = student_data["student_id"]
    student_name = student_data["name"]

    _render_navbar(student_name)

    # Action row
    a1, a2, a3, _ = st.columns([1, 1, 1, 3])
    with a1:
        if st.button("＋ Enroll in Subject", type="primary", use_container_width=True):
            enroll_dialog()
    with a2:
        if st.button("⇄ Switch to Teacher", type="secondary", use_container_width=True):
            st.session_state["login_type"] = "teacher"
            st.rerun()
    with a3:
        if st.button("Sign Out", type="secondary", use_container_width=True):
            st.session_state["is_logged_in"] = False
            del st.session_state.student_data
            st.rerun()

    st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
    st.markdown('<hr style="border:none;border-top:1px solid #E5E7EB;margin:0 0 1.5rem;">', unsafe_allow_html=True)

    # Load data
    with st.spinner("Loading your dashboard…"):
        subjects = get_student_subjects(student_id)
        logs     = get_student_attendance(student_id)

    # Build stats map
    stats_map = {}
    for log in logs:
        sid = log["subject_id"]
        if sid not in stats_map:
            stats_map[sid] = {"total": 0, "attended": 0}
        stats_map[sid]["total"] += 1
        if log.get("is_present"):
            stats_map[sid]["attended"] += 1

    total_all    = sum(s["total"]    for s in stats_map.values()) if stats_map else 0
    attended_all = sum(s["attended"] for s in stats_map.values()) if stats_map else 0
    pct_all      = int(attended_all / total_all * 100) if total_all > 0 else 0

    _render_stats(len(subjects), total_all, attended_all, pct_all)

    # Subjects grid
    _section_header(
        "Your Enrolled Subjects",
        f"{len(subjects)} subject{'s' if len(subjects) != 1 else ''} · Tap a subject for details"
    )

    if not subjects:
        st.markdown("""
        <div style="background:#fff; border:1px solid #E5E7EB; border-radius:12px;
             padding:3rem 2rem; text-align:center;">
          <div style="font-size:2.5rem; margin-bottom:12px;">📚</div>
          <div style="font-size:0.95rem; font-weight:600; color:#374151;
               font-family:'Inter',sans-serif; margin-bottom:6px;">No subjects yet</div>
          <div style="font-size:0.82rem; color:#9CA3AF; font-family:'Inter',sans-serif;">
            Click "Enroll in Subject" above and enter your subject code.
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        cols = st.columns(2, gap="medium")
        for i, sub_node in enumerate(subjects):
            sub  = sub_node["subjects"]
            sid  = sub["subject_id"]
            stat = stats_map.get(sid, {"total": 0, "attended": 0})
            att  = stat["attended"]
            tot  = stat["total"]
            pct  = int(att / tot * 100) if tot > 0 else 0

            # Capture for closure
            _sub  = sub
            _sid  = sid

            def _make_unenroll(sub_ref, sid_ref):
                def unenroll_button():
                    if st.button(
                        "Unenroll",
                        type="tertiary",
                        use_container_width=True,
                        icon=":material/delete_forever:",
                        key=f"unenroll_{sid_ref}",
                    ):
                        unenroll_student_to_subject(student_id, sid_ref)
                        st.toast(f"Unenrolled from {sub_ref['name']}")
                        st.rerun()
                return unenroll_button

            with cols[i % 2]:
                subject_card(
                    name=sub["name"],
                    code=sub["subject_code"],
                    section=sub["section"],
                    stats=[
                        ("📅", "Classes", tot),
                        ("✅", "Attended", att),
                        ("📊", "Attendance", f"{pct}%"),
                    ],
                    footer_callback=_make_unenroll(_sub, _sid),
                )

    footer_dashboard()


# ─── Login / Registration Screen ──────────────────────────────────────────────
def student_screen():
    style_background_dashboard()
    style_base_layout()

    if "student_data" in st.session_state:
        student_dashboard()
        return

    # ── Auth layout ──────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    .sa-auth-wrap {
        max-width: 480px;
        margin: 3rem auto 0;
    }
    .sa-auth-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .sa-auth-header .logo-row {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        margin-bottom: 1rem;
    }
    .sa-auth-header .logo-row span {
        font-size: 1.1rem;
        font-weight: 800;
        color: #4F46E5;
        font-family: 'Inter', sans-serif;
        letter-spacing: -0.03em;
    }
    .sa-auth-header h2 {
        font-size: 1.4rem !important;
        font-weight: 800 !important;
        color: #111827 !important;
        margin-bottom: 6px !important;
    }
    .sa-auth-header p {
        font-size: 0.85rem !important;
        color: #6B7280 !important;
    }
    .sa-auth-card {
        background: #fff;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 2rem;
    }
    .sa-step-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #FFF7ED;
        border: 1px solid #FED7AA;
        color: #C2410C;
        border-radius: 100px;
        padding: 4px 12px;
        font-size: 0.72rem;
        font-weight: 600;
        margin-bottom: 1rem;
        font-family: 'Inter', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

    # Back button row
    back_col, _ = st.columns([1, 3])
    with back_col:
        if st.button("← Home", type="secondary"):
            st.session_state["login_type"] = None
            st.rerun()

    # Centred header
    st.markdown("""
    <div class="sa-auth-header">
      <div class="logo-row">
        <svg width="28" height="28" viewBox="0 0 32 32" fill="none">
          <rect width="32" height="32" rx="8" fill="#4F46E5"/>
          <path d="M8 10h10M8 16h16M8 22h12" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
          <circle cx="24" cy="10" r="3" fill="#06B6D4"/>
        </svg>
        <span>SmartAttend</span>
      </div>
      <h2>Student Login</h2>
      <p>Look into your camera to sign in with Face ID</p>
    </div>
    """, unsafe_allow_html=True)

    # Camera card
    st.markdown('<div class="sa-auth-card">', unsafe_allow_html=True)
    st.markdown('<div class="sa-step-badge">📸 Step 1 — Face Scan</div>', unsafe_allow_html=True)

    show_registration = False
    photo_source = st.camera_input("Position your face in the frame")

    if photo_source:
        img = np.array(Image.open(photo_source))
        with st.spinner("Scanning with AI…"):
            detected, all_ids, num_faces = predict_attendance(img)

            if num_faces == 0:
                st.warning("No face detected. Please move closer to the camera.")
            elif num_faces > 1:
                st.warning("Multiple faces detected. Only one person should be in frame.")
            else:
                if detected:
                    student_id  = list(detected.keys())[0]
                    all_students = get_all_students()
                    student = next(
                        (s for s in all_students if s["student_id"] == student_id), None
                    )
                    if student:
                        st.session_state.is_logged_in  = True
                        st.session_state.user_role     = "student"
                        st.session_state.student_data  = student
                        st.toast(f"Welcome back, {student['name']}! 👋")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.info("Face not recognised. If you're new, register below.")
                    show_registration = True

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Registration ─────────────────────────────────────────────────────────
    if show_registration:
        st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#fff; border:1px solid #E5E7EB; border-radius:16px; padding:2rem;">
          <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase;
               letter-spacing:0.08em; color:#7C3AED; margin-bottom:1rem;
               font-family:'Inter',sans-serif;">✨ New Student — Create Profile</div>
        """, unsafe_allow_html=True)

        new_name = st.text_input("Full Name", placeholder="e.g. Priya Sharma")

        st.markdown("""
        <div style="background:#F0F9FF; border:1px solid #BAE6FD; border-radius:8px;
             padding:10px 14px; margin:0.75rem 0; font-size:0.8rem; color:#0369A1;
             font-family:'Inter',sans-serif;">
          🎙️ <b>Optional:</b> Record your voice to enable voice-based attendance too.
        </div>
        """, unsafe_allow_html=True)

        audio_data = None
        try:
            audio_data = st.audio_input("Record a short phrase (e.g. I am present)")
        except Exception:
            st.error("Audio input unavailable on this device.")

        if st.button("Create My Account", type="primary", use_container_width=True):
            if new_name:
                with st.spinner("Setting up your profile…"):
                    img_reg    = np.array(Image.open(photo_source))
                    encodings  = get_face_embeddings(img_reg)
                    if encodings:
                        face_emb  = encodings[0].tolist()
                        voice_emb = None
                        if audio_data:
                            voice_emb = get_voice_embedding(audio_data.read())
                        response_data = create_student(
                            new_name,
                            face_embedding=face_emb,
                            voice_embedding=voice_emb,
                        )
                        if response_data:
                            train_classifier()
                            st.session_state.is_logged_in = True
                            st.session_state.user_role    = "student"
                            st.session_state.student_data = response_data[0]
                            st.toast(f"Profile created! Welcome, {new_name}! 🎉")
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.error("Could not capture facial features. Please retake the photo.")
            else:
                st.warning("Please enter your full name.")

        st.markdown("</div>", unsafe_allow_html=True)

    footer_dashboard()
