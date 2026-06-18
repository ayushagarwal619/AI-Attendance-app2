"""SmartAttend — Landing Page.
Features: Face Recognition, QR Joining, Attendance Analytics, Secure Records.
Voice Attendance removed from features list per spec.
"""
import streamlit as st
from src.components.header import header_home
from src.components.footer import footer_home
from src.ui.base_layout import style_base_layout, style_background_home

# ── SVG dashboard mockup ──────────────────────────────────────────────────────
_MOCKUP = """
<svg viewBox="0 0 540 360" xmlns="http://www.w3.org/2000/svg"
     style="width:100%;max-width:540px;border-radius:18px;
            box-shadow:0 28px 64px rgba(91,95,248,0.18);display:block;">
  <!-- card bg -->
  <rect width="540" height="360" rx="18" fill="#F8FAFC"/>
  <!-- topbar -->
  <rect width="540" height="46" rx="0" fill="#5B5FF8"/>
  <!-- logo mark in bar -->
  <rect x="14" y="13" width="20" height="20" rx="5" fill="white" opacity="0.9"/>
  <path d="M24 16L19 18.5v4c0 2.6 1.9 5 5 5.6 3.1-.6 5-3 5-5.6v-4L24 16z"
        stroke="#5B5FF8" stroke-width="1.2" fill="none"/>
  <path d="M22 21l1.5 1.5L26 19" stroke="#5B5FF8" stroke-width="1.2"
        stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="40" y="19" width="80" height="8" rx="4" fill="white" opacity="0.65"/>
  <!-- avatar pill -->
  <rect x="460" y="14" width="66" height="18" rx="9" fill="white" opacity="0.15"/>
  <circle cx="470" cy="23" r="7" fill="white" opacity="0.25"/>
  <text x="481" y="27" font-size="8" fill="white" font-family="Inter,sans-serif" font-weight="600">Ankit K.</text>

  <!-- stat cards -->
  <rect x="14" y="62" width="116" height="62" rx="11" fill="white" stroke="#E2E8F0" stroke-width="1"/>
  <rect x="14" y="118" width="116" height="3.5" rx="2" fill="#5B5FF8" opacity="0.7"/>
  <text x="24" y="81" font-size="7.5" fill="#94A3B8" font-family="Inter,sans-serif" font-weight="700" letter-spacing="0.5">SUBJECTS</text>
  <text x="24" y="104" font-size="24" fill="#0F172A" font-family="Inter,sans-serif" font-weight="900">6</text>

  <rect x="140" y="62" width="116" height="62" rx="11" fill="white" stroke="#E2E8F0" stroke-width="1"/>
  <rect x="140" y="118" width="116" height="3.5" rx="2" fill="#06B6D4" opacity="0.7"/>
  <text x="150" y="81" font-size="7.5" fill="#94A3B8" font-family="Inter,sans-serif" font-weight="700" letter-spacing="0.5">CLASSES</text>
  <text x="150" y="104" font-size="24" fill="#0F172A" font-family="Inter,sans-serif" font-weight="900">48</text>

  <rect x="266" y="62" width="116" height="62" rx="11" fill="white" stroke="#E2E8F0" stroke-width="1"/>
  <rect x="266" y="118" width="116" height="3.5" rx="2" fill="#7C3AED" opacity="0.7"/>
  <text x="276" y="81" font-size="7.5" fill="#94A3B8" font-family="Inter,sans-serif" font-weight="700" letter-spacing="0.5">ATTENDED</text>
  <text x="276" y="104" font-size="24" fill="#0F172A" font-family="Inter,sans-serif" font-weight="900">42</text>

  <rect x="392" y="62" width="134" height="62" rx="11" fill="#EEEFFF" stroke="#C7C9FD" stroke-width="1"/>
  <rect x="392" y="118" width="134" height="3.5" rx="2" fill="#22C55E" opacity="0.8"/>
  <text x="402" y="81" font-size="7.5" fill="#64748B" font-family="Inter,sans-serif" font-weight="700" letter-spacing="0.5">ATTENDANCE</text>
  <text x="402" y="104" font-size="24" fill="#5B5FF8" font-family="Inter,sans-serif" font-weight="900">87%</text>

  <!-- subject cards -->
  <rect x="14" y="140" width="248" height="72" rx="11" fill="white" stroke="#E2E8F0" stroke-width="1"/>
  <rect x="14" y="140" width="4" height="72" rx="2" fill="#5B5FF8"/>
  <text x="26" y="158" font-size="9" fill="#0F172A" font-family="Inter,sans-serif" font-weight="700">Data Structures &amp; Algorithms</text>
  <rect x="26" y="163" width="44" height="10" rx="100" fill="#EEEFFF"/>
  <text x="48" y="171" text-anchor="middle" font-size="7" fill="#5B5FF8" font-family="Inter,sans-serif" font-weight="700">CS301</text>
  <text x="26" y="183" font-size="7" fill="#94A3B8" font-family="Inter,sans-serif">Section A · 82% attendance</text>
  <rect x="26" y="196" width="224" height="5" rx="100" fill="#F1F5F9"/>
  <rect x="26" y="196" width="184" height="5" rx="100" fill="#22C55E"/>

  <rect x="276" y="140" width="250" height="72" rx="11" fill="white" stroke="#E2E8F0" stroke-width="1"/>
  <rect x="276" y="140" width="4" height="72" rx="2" fill="#7C3AED"/>
  <text x="288" y="158" font-size="9" fill="#0F172A" font-family="Inter,sans-serif" font-weight="700">Database Management Systems</text>
  <rect x="288" y="163" width="44" height="10" rx="100" fill="#F5F3FF"/>
  <text x="310" y="171" text-anchor="middle" font-size="7" fill="#7C3AED" font-family="Inter,sans-serif" font-weight="700">CS405</text>
  <text x="288" y="183" font-size="7" fill="#94A3B8" font-family="Inter,sans-serif">Section B · 60% attendance</text>
  <rect x="288" y="196" width="226" height="5" rx="100" fill="#F1F5F9"/>
  <rect x="288" y="196" width="136" height="5" rx="100" fill="#F59E0B"/>

  <!-- analytics mini chart -->
  <rect x="14" y="226" width="300" height="120" rx="11" fill="white" stroke="#E2E8F0" stroke-width="1"/>
  <text x="24" y="244" font-size="8" fill="#0F172A" font-family="Inter,sans-serif" font-weight="700">Attendance Trend</text>
  <!-- bar chart -->
  <rect x="30"  y="315" width="18" height="50" rx="4" fill="#5B5FF8" opacity="0.2"/>
  <rect x="30"  y="295" width="18" height="20" rx="4" fill="#5B5FF8" opacity="0.5"/>
  <rect x="30"  y="265" width="18" height="30" rx="4" fill="#5B5FF8"/>
  <rect x="58"  y="305" width="18" height="60" rx="4" fill="#5B5FF8" opacity="0.2"/>
  <rect x="58"  y="285" width="18" height="20" rx="4" fill="#5B5FF8" opacity="0.5"/>
  <rect x="58"  y="260" width="18" height="25" rx="4" fill="#5B5FF8"/>
  <rect x="86"  y="310" width="18" height="55" rx="4" fill="#5B5FF8" opacity="0.2"/>
  <rect x="86"  y="275" width="18" height="35" rx="4" fill="#5B5FF8" opacity="0.5"/>
  <rect x="86"  y="258" width="18" height="17" rx="4" fill="#5B5FF8"/>
  <rect x="114" y="300" width="18" height="65" rx="4" fill="#5B5FF8" opacity="0.2"/>
  <rect x="114" y="278" width="18" height="22" rx="4" fill="#5B5FF8" opacity="0.5"/>
  <rect x="114" y="256" width="18" height="22" rx="4" fill="#5B5FF8"/>
  <rect x="142" y="295" width="18" height="70" rx="4" fill="#5B5FF8" opacity="0.2"/>
  <rect x="142" y="268" width="18" height="27" rx="4" fill="#5B5FF8" opacity="0.5"/>
  <rect x="142" y="253" width="18" height="15" rx="4" fill="#22C55E"/>
  <!-- x labels -->
  <text x="39"  y="330" text-anchor="middle" font-size="6" fill="#94A3B8" font-family="Inter">Jan</text>
  <text x="67"  y="330" text-anchor="middle" font-size="6" fill="#94A3B8" font-family="Inter">Feb</text>
  <text x="95"  y="330" text-anchor="middle" font-size="6" fill="#94A3B8" font-family="Inter">Mar</text>
  <text x="123" y="330" text-anchor="middle" font-size="6" fill="#94A3B8" font-family="Inter">Apr</text>
  <text x="151" y="330" text-anchor="middle" font-size="6" fill="#94A3B8" font-family="Inter">May</text>

  <!-- activity feed -->
  <rect x="328" y="226" width="198" height="120" rx="11" fill="white" stroke="#E2E8F0" stroke-width="1"/>
  <text x="338" y="244" font-size="8" fill="#0F172A" font-family="Inter,sans-serif" font-weight="700">Recent Activity</text>
  <circle cx="342" cy="262" r="6" fill="#DCFCE7"/>
  <text x="342" y="265" text-anchor="middle" font-size="6" fill="#22C55E">✓</text>
  <text x="354" y="265" font-size="7" fill="#334155" font-family="Inter">Present — DSA · 09:15</text>
  <circle cx="342" cy="280" r="6" fill="#DCFCE7"/>
  <text x="342" y="283" text-anchor="middle" font-size="6" fill="#22C55E">✓</text>
  <text x="354" y="283" font-size="7" fill="#334155" font-family="Inter">Present — DBMS · 11:00</text>
  <circle cx="342" cy="298" r="6" fill="#FEE2E2"/>
  <text x="342" y="301" text-anchor="middle" font-size="6" fill="#EF4444">✗</text>
  <text x="354" y="301" font-size="7" fill="#334155" font-family="Inter">Absent — CN · 14:00</text>
  <circle cx="342" cy="316" r="6" fill="#DCFCE7"/>
  <text x="342" y="319" text-anchor="middle" font-size="6" fill="#22C55E">✓</text>
  <text x="354" y="319" font-size="7" fill="#334155" font-family="Inter">Present — OS · 16:00</text>
</svg>"""


# ── Reusable HTML helpers ─────────────────────────────────────────────────────
def _section(eyebrow, title, subtitle=""):
    sub_tag = (f'<div style="font-size:0.9rem;color:#64748B;text-align:center;'
               f'max-width:520px;margin:0 auto 2.5rem;line-height:1.65;'
               f'font-family:Inter,sans-serif;">{subtitle}</div>') if subtitle else ""
    return f"""
<div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;
  letter-spacing:0.1em;color:#5B5FF8;text-align:center;
  font-family:'Inter',sans-serif;margin-bottom:8px;margin-top:4rem;">{eyebrow}</div>
<div style="font-size:clamp(1.55rem,3vw,2.05rem);font-weight:900;letter-spacing:-0.04em;
  color:#0F172A;text-align:center;margin-bottom:0.6rem;
  font-family:'Inter',sans-serif;">{title}</div>
{sub_tag}"""


def home_screen():
    style_background_home()
    style_base_layout()
    header_home()

    # ════════════════════════════════════════════════════════════════════════
    # HERO
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("""
<style>
.hero-badge{display:inline-flex;align-items:center;gap:7px;background:#EEEFFF;
  color:#5B5FF8;border:1px solid #C7C9FD;padding:5px 14px;border-radius:100px;
  font-size:0.75rem;font-weight:700;letter-spacing:0.03em;
  font-family:'Inter',sans-serif;margin-bottom:1.5rem;}
.hero-dot{width:7px;height:7px;background:#5B5FF8;border-radius:50%;
  animation:hpulse 2s infinite;}
@keyframes hpulse{0%,100%{opacity:1;}50%{opacity:0.35;}}
.hero-h1{font-size:clamp(2.2rem,4.5vw,3.55rem)!important;font-weight:900!important;
  letter-spacing:-0.05em!important;line-height:1.06!important;
  color:#0F172A!important;margin-bottom:1.25rem!important;}
.hero-accent{background:linear-gradient(135deg,#5B5FF8,#7C3AED);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.hero-sub{font-size:1.05rem!important;color:#475569!important;
  line-height:1.65!important;max-width:480px;margin-bottom:2rem!important;}
.trust-row{display:flex;align-items:center;gap:10px;margin-top:1.25rem;}
.trust-avs{display:flex;}
.trust-av{width:28px;height:28px;border-radius:50%;border:2px solid #fff;
  margin-left:-8px;font-size:0.62rem;font-weight:800;font-family:'Inter',sans-serif;
  display:flex;align-items:center;justify-content:center;color:#fff;}
.trust-txt{font-size:0.78rem;color:#64748B;font-family:'Inter',sans-serif;}
.trust-txt b{color:#0F172A;}
</style>
<div style="padding:3.5rem 0 1rem;">
  <div class="hero-badge">
    <span class="hero-dot"></span>
    AI-Powered &nbsp;·&nbsp; Face Recognition &nbsp;·&nbsp; QR Attendance
  </div>
  <h1 class="hero-h1">Attendance in<br/><span class="hero-accent">Seconds.</span></h1>
  <p class="hero-sub">
    SmartAttend automates college attendance using AI facial recognition and QR codes —
    no paper, no manual roll call, no proxy.
  </p>
</div>
""", unsafe_allow_html=True)

    lc, rc = st.columns([1.05, 1.2], gap="large")
    with lc:
        c1, c2 = st.columns(2, gap="small")
        with c1:
            if st.button("Student Portal →", type="primary", use_container_width=True):
                st.session_state["login_type"] = "student"
                st.rerun()
        with c2:
            if st.button("Teacher Login →", type="secondary", use_container_width=True):
                st.session_state["login_type"] = "teacher"
                st.rerun()
        st.markdown("""
<div class="trust-row">
  <div class="trust-avs">
    <div class="trust-av" style="background:#5B5FF8;margin-left:0;">RK</div>
    <div class="trust-av" style="background:#7C3AED;">PS</div>
    <div class="trust-av" style="background:#06B6D4;">AM</div>
    <div class="trust-av" style="background:#22C55E;">VJ</div>
  </div>
  <span class="trust-txt"><b>10,000+</b> students using SmartAttend</span>
</div>""", unsafe_allow_html=True)

    with rc:
        st.markdown(_MOCKUP, unsafe_allow_html=True)

    # ── Stats band ───────────────────────────────────────────────────────────
    st.markdown("""
<style>
.stats-band{background:linear-gradient(135deg,#5B5FF8 0%,#7C3AED 100%);
  border-radius:18px;padding:2.25rem 2.5rem;margin:3.5rem 0 2rem;
  display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;}
.sb-item{text-align:center;}
.sb-val{font-size:2rem;font-weight:900;color:#fff;letter-spacing:-0.04em;
  display:block;font-family:'Inter',sans-serif;}
.sb-lbl{font-size:0.72rem;color:rgba(255,255,255,0.62);font-weight:500;
  font-family:'Inter',sans-serif;letter-spacing:0.03em;margin-top:2px;}
@media(max-width:600px){.stats-band{grid-template-columns:repeat(2,1fr);}}
</style>
<div class="stats-band">
  <div class="sb-item"><span class="sb-val">10K+</span><span class="sb-lbl">Students Registered</span></div>
  <div class="sb-item"><span class="sb-val">500+</span><span class="sb-lbl">Classes Daily</span></div>
  <div class="sb-item"><span class="sb-val">98%</span><span class="sb-lbl">Recognition Accuracy</span></div>
  <div class="sb-item"><span class="sb-val">&lt;3s</span><span class="sb-lbl">Avg. Scan Time</span></div>
</div>
""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # FEATURES — exactly 4 as per spec (no Voice Attendance)
    # ════════════════════════════════════════════════════════════════════════
    st.markdown(_section("Features", "What SmartAttend Does",
                         "Four core capabilities that replace manual registers entirely."),
                unsafe_allow_html=True)
    st.markdown("""
<style>
.feat-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin-bottom:1rem;}
@media(max-width:600px){.feat-grid{grid-template-columns:1fr;}}
.feat-card{background:#fff;border:1px solid #E2E8F0;border-radius:16px;
  padding:28px 26px;transition:box-shadow 0.22s,transform 0.22s;}
.feat-card:hover{box-shadow:0 12px 36px rgba(91,95,248,0.1);transform:translateY(-3px);}
.feat-icon{width:48px;height:48px;border-radius:12px;display:flex;align-items:center;
  justify-content:center;font-size:1.3rem;margin-bottom:16px;}
.feat-card h4{font-size:1rem;font-weight:700;color:#0F172A;margin-bottom:8px;
  font-family:'Inter',sans-serif;}
.feat-card p{font-size:0.83rem;color:#64748B;line-height:1.6;
  font-family:'Inter',sans-serif;margin:0;}
</style>
<div class="feat-grid">
  <div class="feat-card">
    <div class="feat-icon" style="background:#EEEFFF;">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="8" r="4" stroke="#5B5FF8" stroke-width="2"/>
        <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" stroke="#5B5FF8" stroke-width="2" stroke-linecap="round"/>
        <path d="M17 13l1.5 1.5L21 12" stroke="#22C55E" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
    <h4>AI Face Recognition</h4>
    <p>Upload a classroom photo — AI scans and marks every enrolled student present or absent in under 3 seconds. No manual input required.</p>
  </div>
  <div class="feat-card">
    <div class="feat-icon" style="background:#F0FDF4;">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
        <rect x="3" y="3" width="7" height="7" rx="1" fill="#22C55E" opacity="0.3"/>
        <rect x="3" y="3" width="7" height="7" rx="1" stroke="#22C55E" stroke-width="1.5"/>
        <rect x="14" y="3" width="7" height="7" rx="1" fill="#22C55E" opacity="0.3"/>
        <rect x="14" y="3" width="7" height="7" rx="1" stroke="#22C55E" stroke-width="1.5"/>
        <rect x="3" y="14" width="7" height="7" rx="1" fill="#22C55E" opacity="0.3"/>
        <rect x="3" y="14" width="7" height="7" rx="1" stroke="#22C55E" stroke-width="1.5"/>
        <rect x="16" y="16" width="3" height="3" rx="0.5" fill="#22C55E"/>
      </svg>
    </div>
    <h4>QR Code Joining</h4>
    <p>Teachers generate a QR code per subject. Students scan once to enroll permanently. Works on any smartphone — no app download needed.</p>
  </div>
  <div class="feat-card">
    <div class="feat-icon" style="background:#FFF7ED;">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
        <rect x="3" y="12" width="4" height="9" rx="1" fill="#F59E0B"/>
        <rect x="10" y="7" width="4" height="14" rx="1" fill="#F59E0B" opacity="0.7"/>
        <rect x="17" y="3" width="4" height="18" rx="1" fill="#F59E0B" opacity="0.4"/>
        <path d="M3 8l5-3 5 4 5-5" stroke="#5B5FF8" stroke-width="1.5"
              stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
    <h4>Attendance Analytics</h4>
    <p>Real-time charts, subject-wise breakdowns, session trends, and low-attendance alerts. Teachers see exactly who needs follow-up.</p>
  </div>
  <div class="feat-card">
    <div class="feat-icon" style="background:#F5F3FF;">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
        <path d="M12 3L4 7v5c0 5.25 3.85 10.16 8 11.35C16.15 22.16 20 17.25 20 12V7L12 3z"
              fill="#7C3AED" opacity="0.15"/>
        <path d="M12 3L4 7v5c0 5.25 3.85 10.16 8 11.35C16.15 22.16 20 17.25 20 12V7L12 3z"
              stroke="#7C3AED" stroke-width="1.5" stroke-linejoin="round"/>
        <path d="M9 12l2 2 4-4" stroke="#7C3AED" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
    <h4>Secure Records</h4>
    <p>All biometric data is encrypted and stored securely. Role-based access ensures teachers and students only see what belongs to them.</p>
  </div>
</div>
""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # HOW IT WORKS
    # ════════════════════════════════════════════════════════════════════════
    st.markdown(_section("How It Works", "Up and Running in 4 Steps",
                         "From first login to your first AI attendance session in under 5 minutes."),
                unsafe_allow_html=True)
    st.markdown("""
<style>
.steps-wrap{background:#fff;border:1px solid #E2E8F0;border-radius:20px;
  padding:2.5rem 2rem;margin:0 0 1rem;}
.steps-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:0;position:relative;}
.steps-grid::before{content:'';position:absolute;top:24px;left:12.5%;right:12.5%;
  height:2px;background:linear-gradient(90deg,#C7C9FD,#DDD6FE);z-index:0;}
@media(max-width:700px){
  .steps-grid{grid-template-columns:1fr 1fr;}
  .steps-grid::before{display:none;}
}
.step-item{text-align:center;padding:0 1rem;position:relative;z-index:1;}
.step-num{width:48px;height:48px;border-radius:50%;
  background:linear-gradient(135deg,#5B5FF8,#7C3AED);
  color:#fff;font-size:0.95rem;font-weight:800;
  display:flex;align-items:center;justify-content:center;
  margin:0 auto 14px;font-family:'Inter',sans-serif;
  box-shadow:0 4px 16px rgba(91,95,248,0.35);}
.step-item h4{font-size:0.9rem;font-weight:700;color:#0F172A;
  margin-bottom:6px;font-family:'Inter',sans-serif;}
.step-item p{font-size:0.78rem;color:#64748B;
  font-family:'Inter',sans-serif;line-height:1.5;margin:0;}
</style>
<div class="steps-wrap">
  <div class="steps-grid">
    <div class="step-item">
      <div class="step-num">1</div>
      <h4>Create Subject</h4>
      <p>Teacher creates a subject with a unique code and section.</p>
    </div>
    <div class="step-item">
      <div class="step-num">2</div>
      <h4>Generate QR</h4>
      <p>A QR code and join link are auto-generated for the subject.</p>
    </div>
    <div class="step-item">
      <div class="step-num">3</div>
      <h4>Students Join</h4>
      <p>Students scan once and are permanently enrolled.</p>
    </div>
    <div class="step-item">
      <div class="step-num">4</div>
      <h4>Track Attendance</h4>
      <p>Upload a photo — AI marks attendance and logs it instantly.</p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Analytics preview callout ─────────────────────────────────────────────
    st.markdown("""
<div style="background:linear-gradient(135deg,#0F172A 0%,#1E293B 100%);
     border-radius:18px;padding:3rem 2.5rem;text-align:center;margin:2rem 0 1rem;">
  <div style="display:inline-flex;align-items:center;gap:8px;background:rgba(91,95,248,0.25);
       color:#C7C9FD;border:1px solid rgba(91,95,248,0.4);padding:4px 14px;
       border-radius:100px;font-size:0.72rem;font-weight:700;letter-spacing:0.05em;
       font-family:'Inter',sans-serif;margin-bottom:1rem;text-transform:uppercase;">
    Analytics &amp; Reporting
  </div>
  <div style="font-size:clamp(1.2rem,2.5vw,1.65rem);font-weight:900;color:#fff;
       letter-spacing:-0.035em;margin-bottom:0.75rem;font-family:'Inter',sans-serif;">
    Know Who Needs Attention — Before It's Too Late
  </div>
  <div style="font-size:0.88rem;color:rgba(255,255,255,0.55);max-width:520px;
       margin:0 auto 1.5rem;font-family:'Inter',sans-serif;line-height:1.65;">
    Per-subject attendance charts, session trends, and automatic low-attendance
    alerts give teachers actionable data every single day.
  </div>
  <div style="display:flex;justify-content:center;gap:2rem;flex-wrap:wrap;">
    <div style="text-align:center;">
      <div style="font-size:1.75rem;font-weight:900;color:#5B5FF8;
           font-family:'Inter',sans-serif;letter-spacing:-0.04em;">98%</div>
      <div style="font-size:0.72rem;color:rgba(255,255,255,0.5);
           font-family:'Inter',sans-serif;">Recognition Rate</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:1.75rem;font-weight:900;color:#22C55E;
           font-family:'Inter',sans-serif;letter-spacing:-0.04em;">50+</div>
      <div style="font-size:0.72rem;color:rgba(255,255,255,0.5);
           font-family:'Inter',sans-serif;">Institutions</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:1.75rem;font-weight:900;color:#F59E0B;
           font-family:'Inter',sans-serif;letter-spacing:-0.04em;">10K+</div>
      <div style="font-size:0.72rem;color:rgba(255,255,255,0.5);
           font-family:'Inter',sans-serif;">Students</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── CTA section ───────────────────────────────────────────────────────────
    st.markdown(_section("Get Started", "Try SmartAttend Today"),
                unsafe_allow_html=True)
    cta_l, cta_m, cta_r, _ = st.columns([1.5, 1, 1, ][::1][:3] if False else [1.5, 1, 1, 1.5])
    with cta_m:
        if st.button("Student Portal →", type="primary", use_container_width=True,
                     key="cta_student"):
            st.session_state["login_type"] = "student"
            st.rerun()
    with cta_r:
        if st.button("Teacher Login →", type="secondary", use_container_width=True,
                     key="cta_teacher"):
            st.session_state["login_type"] = "teacher"
            st.rerun()

    st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
    footer_home()
