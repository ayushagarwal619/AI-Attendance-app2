import streamlit as st
from src.components.header import header_home
from src.components.footer import footer_home
from src.ui.base_layout import style_base_layout, style_background_home


def home_screen():
    style_background_home()
    style_base_layout()
    header_home()

    # ── Hero ─────────────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    .sa-hero {
        text-align: center;
        padding: 5rem 1rem 3rem;
        max-width: 780px;
        margin: 0 auto;
    }
    .sa-hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #EEF2FF;
        color: #4F46E5;
        border: 1px solid #C7D2FE;
        padding: 5px 14px;
        border-radius: 100px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        margin-bottom: 1.5rem;
    }
    .sa-hero h1 {
        font-size: clamp(2.4rem, 5vw, 3.75rem) !important;
        font-weight: 900 !important;
        letter-spacing: -0.05em !important;
        color: #111827 !important;
        line-height: 1.05 !important;
        margin-bottom: 1.25rem !important;
    }
    .sa-hero-accent { color: #4F46E5; }
    .sa-hero p {
        font-size: 1.1rem !important;
        color: #4B5563 !important;
        max-width: 560px;
        margin: 0 auto 2.25rem;
        line-height: 1.65;
    }
    .sa-hero-actions {
        display: flex;
        gap: 12px;
        justify-content: center;
        flex-wrap: wrap;
    }
    .sa-hero-img {
        margin-top: 3.5rem;
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        border-radius: 20px;
        padding: 2.5rem 2rem;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 1.5rem;
        flex-wrap: wrap;
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
    }
    .sa-stat-pill {
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        text-align: center;
        min-width: 130px;
    }
    .sa-stat-pill .val {
        font-size: 1.75rem;
        font-weight: 800;
        color: #fff;
        display: block;
        letter-spacing: -0.03em;
    }
    .sa-stat-pill .lbl {
        font-size: 0.75rem;
        color: rgba(255,255,255,0.7);
        font-weight: 500;
        letter-spacing: 0.02em;
    }
    </style>
    <div class="sa-hero">
      <div class="sa-hero-badge">
        <svg width="12" height="12" fill="#4F46E5" viewBox="0 0 12 12">
          <circle cx="6" cy="6" r="5"/>
        </svg>
        AI-Powered &nbsp;&bull;&nbsp; Face &amp; Voice Recognition
      </div>
      <h1>Attendance in <span class="sa-hero-accent">Seconds</span>,<br/>Not Minutes.</h1>
      <p>SmartAttend uses facial recognition and QR technology to automate attendance for colleges and universities — no paper, no manual entry.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── CTA Buttons ──────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns([1.5, 1, 1.5])
    with c2:
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    col_l, col_s, col_t, col_r = st.columns([1.2, 1, 1, 1.2])
    with col_s:
        if st.button("Student Portal →", type="primary", use_container_width=True):
            st.session_state["login_type"] = "student"
            st.rerun()
    with col_t:
        if st.button("Teacher Portal →", type="secondary", use_container_width=True):
            st.session_state["login_type"] = "teacher"
            st.rerun()

    # ── Hero Stats Banner ────────────────────────────────────────────────────
    st.markdown("""
    <div class="sa-hero-img">
      <div class="sa-stat-pill">
        <span class="val">10K+</span>
        <span class="lbl">Students</span>
      </div>
      <div class="sa-stat-pill">
        <span class="val">500+</span>
        <span class="lbl">Classes Daily</span>
      </div>
      <div class="sa-stat-pill">
        <span class="val">98%</span>
        <span class="lbl">Accuracy</span>
      </div>
      <div class="sa-stat-pill">
        <span class="val">3 sec</span>
        <span class="lbl">Avg. Scan Time</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Features Section ─────────────────────────────────────────────────────
    st.markdown("""
    <style>
    .sa-section-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #4F46E5;
        text-align: center;
        margin-bottom: 8px;
        margin-top: 5rem;
    }
    .sa-section-title {
        font-size: clamp(1.6rem, 3vw, 2.25rem);
        font-weight: 800;
        letter-spacing: -0.04em;
        color: #111827;
        text-align: center;
        margin-bottom: 0.75rem;
    }
    .sa-section-sub {
        font-size: 0.95rem;
        color: #6B7280;
        text-align: center;
        max-width: 520px;
        margin: 0 auto 3rem;
        line-height: 1.6;
    }
    .sa-feat-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 16px;
        margin-bottom: 1rem;
    }
    .sa-feat-card {
        background: #fff;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 24px;
        transition: box-shadow 0.2s ease, transform 0.2s ease;
    }
    .sa-feat-card:hover {
        box-shadow: 0 8px 30px rgba(79,70,229,0.1);
        transform: translateY(-2px);
    }
    .sa-feat-icon {
        width: 44px;
        height: 44px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        margin-bottom: 14px;
    }
    .sa-feat-card h4 {
        font-size: 0.95rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 6px;
        font-family: 'Inter', sans-serif;
    }
    .sa-feat-card p {
        font-size: 0.82rem;
        color: #6B7280;
        line-height: 1.55;
        font-family: 'Inter', sans-serif;
        margin: 0;
    }
    </style>
    <div class="sa-section-label">Features</div>
    <div class="sa-section-title">Everything You Need</div>
    <div class="sa-section-sub">
      Built for real classrooms. Designed to replace clipboards and manual registers.
    </div>
    <div class="sa-feat-grid">
      <div class="sa-feat-card">
        <div class="sa-feat-icon" style="background:#EEF2FF;">🤖</div>
        <h4>Face Recognition</h4>
        <p>Automatically identify and mark students present using advanced facial recognition — no manual input needed.</p>
      </div>
      <div class="sa-feat-card">
        <div class="sa-feat-icon" style="background:#F0FDF4;">📱</div>
        <h4>QR Code Joining</h4>
        <p>Students join subjects instantly by scanning a QR code. Works on any smartphone — no app required.</p>
      </div>
      <div class="sa-feat-card">
        <div class="sa-feat-icon" style="background:#FFF7ED;">📊</div>
        <h4>Live Analytics</h4>
        <p>Track attendance trends, identify low-attendance students, and generate reports in one click.</p>
      </div>
      <div class="sa-feat-card">
        <div class="sa-feat-icon" style="background:#F0F9FF;">🎙️</div>
        <h4>Voice Attendance</h4>
        <p>Record classroom audio and let AI identify who said "Present" — a second layer of verification.</p>
      </div>
      <div class="sa-feat-card">
        <div class="sa-feat-icon" style="background:#FFF1F2;">⚡</div>
        <h4>Instant Reports</h4>
        <p>Session-by-session attendance logs with present/absent breakdown, exportable at any time.</p>
      </div>
      <div class="sa-feat-card">
        <div class="sa-feat-icon" style="background:#F5F3FF;">🔒</div>
        <h4>Secure & Private</h4>
        <p>All biometric data is encrypted. Role-based access keeps teacher and student data completely separate.</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── How It Works ─────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    .sa-steps {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 0;
        margin: 3rem 0;
        position: relative;
    }
    .sa-step {
        text-align: center;
        padding: 2rem 1.5rem;
        position: relative;
    }
    .sa-step-num {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: linear-gradient(135deg, #4F46E5, #7C3AED);
        color: white;
        font-size: 0.9rem;
        font-weight: 800;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 14px;
        font-family: 'Inter', sans-serif;
        box-shadow: 0 4px 14px rgba(79,70,229,0.3);
    }
    .sa-step h4 {
        font-size: 0.9rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 6px;
        font-family: 'Inter', sans-serif;
    }
    .sa-step p {
        font-size: 0.8rem;
        color: #6B7280;
        font-family: 'Inter', sans-serif;
        margin: 0;
    }
    </style>
    <div class="sa-section-label">How It Works</div>
    <div class="sa-section-title">Up and Running in 4 Steps</div>
    <div class="sa-section-sub">From setup to first attendance session in under 5 minutes.</div>
    <div class="sa-steps">
      <div class="sa-step">
        <div class="sa-step-num">1</div>
        <h4>Create a Subject</h4>
        <p>Teacher sets up the subject with a unique code and section.</p>
      </div>
      <div class="sa-step">
        <div class="sa-step-num">2</div>
        <h4>Share QR Code</h4>
        <p>A unique QR link is generated for students to scan and join.</p>
      </div>
      <div class="sa-step">
        <div class="sa-step-num">3</div>
        <h4>Students Join</h4>
        <p>Students scan the QR once and are enrolled permanently.</p>
      </div>
      <div class="sa-step">
        <div class="sa-step-num">4</div>
        <h4>Take Attendance</h4>
        <p>Upload a photo, run face analysis, attendance is saved instantly.</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Testimonial / Social Proof ────────────────────────────────────────────
    st.markdown("""
    <div style="background:linear-gradient(135deg,#4F46E5 0%,#7C3AED 100%);
         border-radius:20px; padding:3rem 2rem; text-align:center; margin:2rem 0 3rem;">
      <div style="font-size:1.5rem; font-weight:800; color:#fff; letter-spacing:-0.03em;
                  margin-bottom:0.75rem; font-family:'Inter',sans-serif;">
        Trusted by 10,000+ Students Across 50+ Institutions
      </div>
      <div style="font-size:0.9rem; color:rgba(255,255,255,0.75); max-width:480px;
                  margin:0 auto; font-family:'Inter',sans-serif; line-height:1.6;">
        SmartAttend replaced our paper registers completely.
        Attendance is now done before the lecture even starts.
      </div>
    </div>
    """, unsafe_allow_html=True)

    footer_home()
