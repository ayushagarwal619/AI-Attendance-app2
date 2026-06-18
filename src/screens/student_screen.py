"""SmartAttend — Student Screen.
Redesigned with premium SaaS styling, pure HTML/CSS responsive bar charts,
timeline component, attendance insights, and responsive grid layouts.
"""
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
import math
from datetime import datetime, timedelta
from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card # kept for safety/compatibility

# ── Inline logo SVG ───────────────────────────────────────────────────────────
_LOGO = """<svg width="30" height="30" viewBox="0 0 36 36" fill="none">
  <rect width="36" height="36" rx="9" fill="#6366F1"/>
  <path d="M18 7L9 11v8c0 5.25 3.85 10.16 9 11.35C23.15 29.16 27 24.25 27 19v-8l-9-4z"
        fill="white" fill-opacity="0.15"/>
  <path d="M18 7L9 11v8c0 5.25 3.85 10.16 9 11.35C23.15 29.16 27 24.25 27 19v-8l-9-4z"
        stroke="white" stroke-width="1.5" stroke-linejoin="round"/>
  <path d="M14 18l2.8 2.8L22.5 15" stroke="white" stroke-width="2"
        stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""


# ── Top navbar ────────────────────────────────────────────────────────────────
def _topnav(name, role="Student"):
    initial = (name[:1].upper()) if name else "S"
    st.markdown(f"""
<style>
.stn{{display:flex;align-items:center;justify-content:space-between;
  padding:0.9rem 0;border-bottom:1px solid #E2E8F0;margin-bottom:1.75rem;}}
.stn-brand{{display:flex;align-items:center;gap:10px;}}
.stn-brand .wm{{font-family:'Inter',sans-serif;font-size:0.97rem;font-weight:800;
  color:#6366F1;letter-spacing:-0.03em;}}
.stn-right{{display:flex;align-items:center;gap:12px;}}
.stn-av{{width:36px;height:36px;border-radius:50%;
  background:linear-gradient(135deg,#6366F1,#818CF8);color:#fff;font-size:0.8rem;
  font-weight:800;display:flex;align-items:center;justify-content:center;
  font-family:'Inter',sans-serif;flex-shrink:0;}}
.stn-uname{{font-size:0.85rem;font-weight:600;color:#0F172A;
  font-family:'Inter',sans-serif;display:block;}}
.stn-urole{{font-size:0.72rem;color:#94A3B8;font-family:'Inter',sans-serif;display:block;}}
</style>
<div class="stn">
  <div class="stn-brand">{_LOGO}<span class="wm">SmartAttend</span></div>
  <div class="stn-right">
    <div class="stn-av">{initial}</div>
    <div><span class="stn-uname">{name}</span><span class="stn-urole">{role}</span></div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Section header ────────────────────────────────────────────────────────────
def _sec(title, sub=""):
    sub_html = (f'<p style="margin:4px 0 0;font-size:0.8rem;color:#64748B;'
                f'font-family:Inter,sans-serif;">{sub}</p>') if sub else ""
    st.markdown(
        f'<div style="margin-bottom:1rem;">'
        f'<h2 style="margin:0;font-size:1.08rem;font-weight:700;color:#0F172A;'
        f'font-family:Inter,sans-serif;letter-spacing:-0.02em;">{title}</h2>'
        f'{sub_html}</div>',
        unsafe_allow_html=True,
    )


# ── Pure HTML/CSS Bar Chart Renderer ──────────────────────────────────────────
def _render_html_bar_chart(stats_map, subjects_map, pct_all):
    if not stats_map:
        return """
        <div style="background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 16px; padding: 32px; text-align: center; color: var(--text-secondary);">
          No attendance records found to plot.
        </div>
        """
        
    bars_html = ""
    for sid, v in stats_map.items():
        tot = v["total"]
        att = v["attended"]
        pct = int(att / tot * 100) if tot > 0 else 0
        full_name = subjects_map.get(sid, {}).get("name", str(sid)) if subjects_map.get(sid) else str(sid)
        short_name = full_name[:12] + "..." if len(full_name) > 12 else full_name
        
        # Semantic status classes & colors
        if pct >= 85:
            color = "#22C55E"
            status_class = "safe"
        elif pct >= 75:
            color = "#F59E0B"
            status_class = "warning"
        else:
            color = "#EF4444"
            status_class = "critical"
            
        bars_html += f"""
        <div class="chart-bar-wrapper">
          <div class="chart-bar {status_class}" style="--bar-height: {pct}%; background-color: {color};">
            <span class="tooltip-text">
              <strong>{full_name}</strong><br/>
              Attendance: {pct}%<br/>
              Classes: {att} / {tot}
            </span>
          </div>
          <div class="chart-x-label" title="{full_name}">{short_name}</div>
        </div>
        """

    avg_top = 100 - pct_all
    
    chart_html = f"""
    <style>
    .chart-container-wrapper {{
      position: relative;
      padding: 24px;
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
      margin-bottom: 24px;
    }}
    .chart-container-title {{
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0;
    }}
    .chart-container-sub {{
      font-size: 13px;
      color: var(--text-secondary);
      margin: 2px 0 20px 0;
    }}
    .chart-container {{
      position: relative;
      height: 240px;
      margin-top: 10px;
      border-bottom: 1.5px solid var(--text-secondary);
      display: flex;
      align-items: flex-end;
      justify-content: space-around;
      padding-left: 45px;
    }}
    .chart-y-axis {{
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: 40px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      font-size: 10px;
      color: var(--text-secondary);
      text-align: right;
      padding-right: 8px;
    }}
    .chart-gridline {{
      position: absolute;
      left: 45px;
      right: 0;
      height: 1px;
      background-color: rgba(226, 232, 240, 0.6);
      z-index: 1;
    }}
    .chart-ref-line {{
      position: absolute;
      left: 45px;
      right: 0;
      border-top: 1.5px dashed;
      z-index: 2;
    }}
    .chart-ref-label {{
      position: absolute;
      right: 10px;
      font-size: 9px;
      font-weight: 600;
      padding: 2px 6px;
      border-radius: 4px;
      transform: translateY(-50%);
      z-index: 3;
    }}
    .chart-bar-wrapper {{
      display: flex;
      flex-direction: column;
      align-items: center;
      flex: 1;
      max-width: 80px;
      height: 100%;
      justify-content: flex-end;
      position: relative;
      z-index: 4;
    }}
    @keyframes barGrow {{
      from {{ height: 0%; }}
      to {{ height: var(--bar-height); }}
    }}
    .chart-bar {{
      width: 36px;
      border-top-left-radius: 6px;
      border-top-right-radius: 6px;
      height: 0%;
      animation: barGrow 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards;
      position: relative;
      cursor: pointer;
      transition: filter 0.2s;
    }}
    .chart-bar:hover {{
      filter: brightness(0.92);
    }}
    .chart-bar .tooltip-text {{
      visibility: hidden;
      width: 150px;
      background-color: #0F172A;
      color: #FFFFFF;
      text-align: left;
      border-radius: 6px;
      padding: 10px;
      position: absolute;
      z-index: 100;
      bottom: 115%;
      left: 50%;
      transform: translateX(-50%);
      opacity: 0;
      transition: opacity 0.2s, transform 0.2s;
      font-size: 11px;
      line-height: 1.4;
      box-shadow: 0 4px 16px rgba(0,0,0,0.15);
      pointer-events: none;
    }}
    .chart-bar .tooltip-text::after {{
      content: "";
      position: absolute;
      top: 100%;
      left: 50%;
      margin-left: -5px;
      border-width: 5px;
      border-style: solid;
      border-color: #0F172A transparent transparent transparent;
    }}
    .chart-bar:hover .tooltip-text {{
      visibility: visible;
      opacity: 1;
    }}
    .chart-x-label {{
      font-size: 11px;
      color: var(--text-secondary);
      margin-top: 8px;
      text-align: center;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      width: 100%;
    }}
    </style>
    
    <div class="chart-container-wrapper">
      <h3 class="chart-container-title">Attendance by Subject</h3>
      <p class="chart-container-sub">This semester</p>
      
      <div class="chart-container">
        <div class="chart-y-axis">
          <span>100%</span>
          <span>75%</span>
          <span>50%</span>
          <span>25%</span>
          <span>0%</span>
        </div>
        
        <div class="chart-gridline" style="top: 0%;"></div>
        <div class="chart-gridline" style="top: 25%;"></div>
        <div class="chart-gridline" style="top: 50%;"></div>
        <div class="chart-gridline" style="top: 75%;"></div>
        <div class="chart-gridline" style="top: 100%;"></div>
        
        <div class="chart-ref-line" style="top: 15%; border-color: var(--success-color);"></div>
        <span class="chart-ref-label" style="top: 15%; background-color: #D1FAE5; color: var(--success-color);">Target (85%)</span>
        
        <div class="chart-ref-line" style="top: 25%; border-color: var(--primary-color);"></div>
        <span class="chart-ref-label" style="top: 25%; background-color: #EEF2FF; color: var(--primary-color);">Min. Required (75%)</span>
        
        <div class="chart-ref-line" style="top: {avg_top}%; border-color: var(--secondary-color); border-style: dotted;"></div>
        <span class="chart-ref-label" style="top: {avg_top}%; background-color: rgba(226, 232, 240, 0.85); color: var(--text-secondary); left: 55px; right: auto;">Average ({pct_all}%)</span>
        
        {bars_html}
      </div>
    </div>
    """
    return chart_html


# ════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
def student_dashboard():
    sd         = st.session_state.student_data
    student_id = sd["student_id"]
    name       = sd["name"]

    # Retrieve all teachers once to map teacher_id to name
    try:
        from src.database.config import supabase
        teachers_data = supabase.table("teachers").select("teacher_id, name").execute().data
        teachers_map = {t["teacher_id"]: t["name"] for t in teachers_data}
    except Exception:
        teachers_map = {}

    # Render navbar
    _topnav(name, "Student")

    # Action bar
    t1, t2, t3, _ = st.columns([1.2, 1.2, 1.2, 4.4], gap="small")
    with t1:
        if st.button("＋ Enroll Subject", type="primary", use_container_width=True, key="action_enroll"):
            enroll_dialog()
    with t2:
        if st.button("⇄ Teacher Mode", type="secondary", use_container_width=True, key="action_teacher"):
            st.session_state["login_type"] = "teacher"
            st.rerun()
    with t3:
        if st.button("Sign Out", type="secondary", use_container_width=True, key="action_signout"):
            st.session_state["is_logged_in"] = False
            del st.session_state.student_data
            st.rerun()

    # Load data
    with st.spinner("Loading your dashboard…"):
        subjects = get_student_subjects(student_id)
        logs     = get_student_attendance(student_id)

    # Compute calculations
    stats_map    = {}
    subjects_map = {}
    for sn in subjects:
        s = sn.get("subjects", {})
        if s:
            subjects_map[s.get("subject_id")] = s
    for log in logs:
        sid = log["subject_id"]
        if sid not in stats_map:
            stats_map[sid] = {"total": 0, "attended": 0}
        stats_map[sid]["total"] += 1
        if log.get("is_present"):
            stats_map[sid]["attended"] += 1

    total_all    = sum(v["total"]    for v in stats_map.values()) if stats_map else 0
    attended_all = sum(v["attended"] for v in stats_map.values()) if stats_map else 0
    pct_all      = int(attended_all / total_all * 100) if total_all > 0 else 0

    # Greeting based on local time
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good Morning 👋"
    elif current_hour < 18:
        greeting = "Good Afternoon 👋"
    else:
        greeting = "Good Evening 👋"

    # Dynamic motivational hero message
    if pct_all >= 85:
        motivation_msg = "Excellent attendance. Keep it up."
    elif pct_all >= 75:
        motivation_msg = "You're on track."
    else:
        motivation_msg = "Attendance needs attention."

    # Hero card status badge info
    if pct_all >= 85:
        status_label = "Safe"
        status_class = "safe"
    elif pct_all >= 75:
        status_label = "Warning"
        status_class = "warning"
    else:
        status_label = "At Risk"
        status_class = "at-risk"

    # Current date and day
    today_str = datetime.now().strftime("%A, %d %B %Y")

    # Compute attendance momentum (trend)
    now = datetime.now()
    two_weeks_ago = now - timedelta(days=14)
    four_weeks_ago = now - timedelta(days=28)
    
    recent_total = 0
    recent_attended = 0
    older_total = 0
    older_attended = 0
    
    for log in logs:
        ts_raw = log.get("timestamp")
        if not ts_raw:
            continue
        try:
            log_dt = datetime.fromisoformat(ts_raw)
            if log_dt.tzinfo is not None:
                log_dt = log_dt.replace(tzinfo=None)
            
            naive_now = now.replace(tzinfo=None)
            naive_2w = two_weeks_ago.replace(tzinfo=None)
            naive_4w = four_weeks_ago.replace(tzinfo=None)
            
            if naive_4w <= log_dt < naive_2w:
                older_total += 1
                if log.get("is_present"):
                    older_attended += 1
            elif naive_2w <= log_dt <= naive_now:
                recent_total += 1
                if log.get("is_present"):
                    recent_attended += 1
        except Exception:
            pass

    recent_rate = (recent_attended / recent_total) if recent_total > 0 else 0.0
    older_rate = (older_attended / older_total) if older_total > 0 else 0.0

    if recent_total == 0 and older_total == 0:
        trend_str = "Stable"
        trend_color = "#64748B"
        trend_arrow = "→"
    else:
        diff = recent_rate - older_rate
        if diff > 0.01:
            trend_str = "Improving"
            trend_color = "#22C55E"
            trend_arrow = "↑"
        elif diff < -0.01:
            trend_str = "Declining"
            trend_color = "#EF4444"
            trend_arrow = "↓"
        else:
            trend_str = "Stable"
            trend_color = "#64748B"
            trend_arrow = "→"

    # HTML inject header & hero & stylesheet & scripts
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {{
  --primary-color: #6366F1;
  --secondary-color: #818CF8;
  --success-color: #22C55E;
  --warning-color: #F59E0B;
  --danger-color: #EF4444;
  --background-color: #F8FAFC;
  --card-bg: #FFFFFF;
  --text-primary: #0F172A;
  --text-secondary: #64748B;
  --text-hint: #9CA3AF;
  --border-color: #E2E8F0;
}}

/* Global resets and chrome removal */
#MainMenu, footer, header {{
  visibility: hidden !important;
  height: 0 !important;
}}

.block-container {{
  padding-top: 1rem !important;
  padding-left: 1.5rem !important;
  padding-right: 1.5rem !important;
  background-color: var(--background-color);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}}

/* Sections spacing */
.student-dashboard-root {{
  display: flex;
  flex-direction: column;
  gap: 24px;
}}

/* Animations */
@keyframes fadeIn {{
  from {{ opacity: 0; transform: translateY(12px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}

.animate-fade-in {{
  animation: fadeIn 0.4s ease-out forwards;
}}

.hover-lift {{
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}}
.hover-lift:hover {{
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.12);
  border-color: var(--primary-color);
}}

/* Hero Card Styles */
.hero-card {{
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
  border-radius: 24px;
  padding: 32px;
  color: #FFFFFF;
  box-shadow: 0 8px 32px rgba(99, 102, 241, 0.15);
}}
.hero-container {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 24px;
}}
.hero-left {{
  flex: 1;
  min-width: 280px;
}}
.hero-greeting {{
  font-size: 24px;
  font-weight: 500;
  opacity: 0.9;
  display: block;
}}
.hero-student-name {{
  font-size: 32px;
  font-weight: 700;
  display: block;
  margin-top: 4px;
  letter-spacing: -0.02em;
}}
.hero-motivation {{
  font-size: 15px;
  opacity: 0.85;
  margin: 12px 0 20px 0;
}}
.hero-meta-row {{
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  opacity: 0.75;
  flex-wrap: wrap;
}}
.hero-meta-divider {{
  opacity: 0.5;
}}
.hero-right {{
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}}
.circular-progress-container {{
  position: relative;
  width: 120px;
  height: 120px;
}}
.progress-ring {{
  transform: rotate(-90deg);
}}
.progress-ring-fill {{
  transition: stroke-dashoffset 1s ease-out;
}}
.progress-text-container {{
  position: absolute;
  top: 0;
  left: 0;
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}}
.progress-pct-value {{
  font-size: 24px;
  font-weight: 700;
}}
.status-badge-hero {{
  font-size: 11px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 9999px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}}
.status-badge-hero.safe {{
  background-color: var(--success-color);
  color: #FFFFFF;
}}
.status-badge-hero.warning {{
  background-color: var(--warning-color);
  color: #FFFFFF;
}}
.status-badge-hero.at-risk {{
  background-color: var(--danger-color);
  color: #FFFFFF;
}}

/* Quick Actions Cards */
.action-card {{
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(226, 232, 240, 0.8);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  height: 110px;
  justify-content: center;
  transition: all 0.25s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}}
.action-card:hover {{
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.1);
  border-color: var(--primary-color);
  background: var(--card-bg);
}}
.action-icon {{
  font-size: 20px;
  margin-bottom: 6px;
}}
.action-title {{
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}}
.action-sub {{
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 2px;
}}

/* Custom styling for the Streamlit download button */
div[data-testid="stDownloadButton"] > button {{
  background: rgba(255, 255, 255, 0.7) !important;
  backdrop-filter: blur(8px) !important;
  -webkit-backdrop-filter: blur(8px) !important;
  border: 1px solid rgba(226, 232, 240, 0.8) !important;
  border-radius: 12px !important;
  padding: 16px !important;
  display: flex !important;
  flex-direction: column !important;
  height: 110px !important;
  justify-content: center !important;
  align-items: flex-start !important;
  text-align: left !important;
  transition: all 0.25s ease !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02) !important;
  color: var(--text-primary) !important;
  line-height: 1.3 !important;
  width: 100% !important;
}}
div[data-testid="stDownloadButton"] > button:hover {{
  transform: translateY(-3px) !important;
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.1) !important;
  border-color: var(--primary-color) !important;
  background: var(--card-bg) !important;
}}
div[data-testid="stDownloadButton"] > button p {{
  margin: 0 !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  color: var(--text-primary) !important;
}}
div[data-testid="stDownloadButton"] > button::after {{
  content: 'Save history to local device';
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 2px;
  font-weight: 400;
}}

/* KPI Card Grid */
.kpi-card {{
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  height: 100%;
}}
.kpi-icon-container {{
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--accent-light, #EEF2FF);
  color: var(--primary-color);
  margin-bottom: 12px;
  font-size: 18px;
}}
.kpi-value {{
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}}
.kpi-label {{
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-top: 4px;
}}

/* Insights Grid */
.insights-grid {{
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}}
.insight-tile {{
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}}
.insight-header {{
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}}
.insight-icon {{
  font-size: 16px;
}}
.insight-label {{
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}}
.insight-val {{
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}}
.insight-desc {{
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 4px;
}}

/* Subject Performance Card */
.subject-card {{
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 250px;
  justify-content: space-between;
  transition: all 0.25s ease;
}}
.subject-card:hover {{
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.12);
}}
.subject-card::before {{
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: 4px;
}}
.subject-card.safe::before {{ background-color: var(--success-color); }}
.subject-card.warning::before {{ background-color: var(--warning-color); }}
.subject-card.critical::before {{ background-color: var(--danger-color); }}

.subject-header {{
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}}
.subject-title {{
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  padding-right: 12px;
}}
.status-badge-small {{
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 9999px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  flex-shrink: 0;
}}
.status-badge-small.safe {{
  background-color: #D1FAE5;
  color: var(--success-color);
}}
.status-badge-small.warning {{
  background-color: #FEF3C7;
  color: var(--warning-color);
}}
.status-badge-small.critical {{
  background-color: #FEE2E2;
  color: var(--danger-color);
}}

.subject-body {{
  display: flex;
  flex-direction: column;
  margin-top: 10px;
  flex-grow: 1;
}}
.subject-meta {{
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 2px;
}}
.card-divider {{
  border: 0;
  border-top: 1px solid var(--border-color);
  margin: 12px 0;
}}
.progress-label-row {{
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 4px;
}}
.pct-val.safe {{ color: var(--success-color); font-weight: 600; }}
.pct-val.warning {{ color: var(--warning-color); font-weight: 600; }}
.pct-val.critical {{ color: var(--danger-color); font-weight: 600; }}

/* Progress Fill Animation */
@keyframes prog-fill {{
  from {{ width: 0%; }}
  to {{ width: var(--target-width); }}
}}
.progress-bar-track {{
  height: 6px;
  background-color: var(--border-color);
  border-radius: 9999px;
  overflow: hidden;
  margin-bottom: 14px;
}}
.progress-bar-fill {{
  height: 100%;
  border-radius: 9999px;
  animation: prog-fill 0.8s ease-out forwards;
}}
.progress-bar-fill.safe {{
  background: linear-gradient(90deg, #A7F3D0 0%, var(--success-color) 100%);
}}
.progress-bar-fill.warning {{
  background: linear-gradient(90deg, #FDE68A 0%, var(--warning-color) 100%);
}}
.progress-bar-fill.critical {{
  background: linear-gradient(90deg, #FCA5A5 0%, var(--danger-color) 100%);
}}

.subject-footer-stats {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  border-top: 1px solid var(--border-color);
  padding-top: 10px;
  text-align: center;
}}
.footer-stat-col {{
  display: flex;
  flex-direction: column;
}}
.footer-stat-col:not(:last-child) {{
  border-right: 1px solid var(--border-color);
}}
.stat-num {{
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
}}
.stat-num.text-red {{
  color: var(--danger-color);
}}
.stat-lbl {{
  font-size: 10px;
  color: var(--text-secondary);
  margin-top: 2px;
}}

/* Custom styling to place Unenroll button below cards neatly */
div[data-testid="stButton"] button[key^="unenroll_"] {{
  background-color: transparent !important;
  color: var(--text-secondary) !important;
  border: 1px solid var(--border-color) !important;
  border-radius: 8px !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  padding: 6px 12px !important;
  height: auto !important;
  margin-top: 8px !important;
  transition: all 0.2s ease !important;
  width: 100% !important;
}}
div[data-testid="stButton"] button[key^="unenroll_"]:hover {{
  color: var(--danger-color) !important;
  border-color: var(--danger-color) !important;
  background-color: rgba(239, 68, 68, 0.05) !important;
}}

/* Custom styling for top Actions Buttons */
div[data-testid="stButton"] button[key^="action_"] {{
  border-radius: 8px !important;
  font-weight: 500 !important;
  font-size: 13px !important;
  transition: all 0.2s ease !important;
}}

/* Timeline Styles */
.timeline-container {{
  display: flex;
  flex-direction: column;
}}
.timeline-row {{
  display: flex;
  align-items: flex-start;
  padding-bottom: 16px;
  position: relative;
}}
.timeline-left {{
  width: 36px;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  align-self: stretch;
}}
.timeline-dot {{
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 700;
  z-index: 2;
  margin-top: 2px;
}}
.timeline-dot.present {{
  background-color: rgba(34, 197, 94, 0.15);
  color: var(--success-color);
}}
.timeline-dot.absent {{
  background-color: rgba(239, 68, 68, 0.15);
  color: var(--danger-color);
}}
.timeline-line {{
  position: absolute;
  top: 22px;
  bottom: -16px;
  width: 1.5px;
  background-color: var(--border-color);
  z-index: 1;
}}
.timeline-row:last-child .timeline-line {{
  display: none;
}}
.timeline-content {{
  flex: 1;
  padding-left: 12px;
}}
.timeline-title-row {{
  display: flex;
  justify-content: space-between;
  align-items: center;
}}
.timeline-subject {{
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}}
.timeline-meta {{
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 2px;
}}
.status-pill {{
  font-size: 10px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 9999px;
}}
.status-pill.present {{
  background-color: rgba(34, 197, 94, 0.1);
  color: var(--success-color);
}}
.status-pill.absent {{
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--danger-color);
}}
.empty-timeline {{
  text-align: center;
  padding: 30px;
  color: var(--text-secondary);
}}

@keyframes timelineFadeIn {{
  from {{ opacity: 0; transform: translateY(8px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}
.animate-timeline-item {{
  opacity: 0;
  animation: timelineFadeIn 0.3s ease-out forwards;
}}

/* Empty State Cards */
.empty-state-container {{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  background: var(--card-bg);
  border: 2px dashed var(--border-color);
  border-radius: 16px;
  text-align: center;
  max-width: 480px;
  margin: 20px auto;
}}
.empty-state-svg {{
  color: var(--text-secondary);
  margin-bottom: 16px;
  animation: float 3s ease-in-out infinite;
}}
@keyframes float {{
  0%, 100% {{ transform: translateY(0); }}
  50% {{ transform: translateY(-4px); }}
}}
.empty-state-title {{
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}}
.empty-state-subtitle {{
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
}}
</style>

<div class="student-dashboard-root animate-fade-in" id="student-dashboard-root">
  
  <!-- SECTION 1: HERO CARD -->
  <div class="hero-card">
    <div class="hero-container">
      <div class="hero-left">
        <span class="hero-greeting">{greeting}</span>
        <span class="hero-student-name">{name}</span>
        <p class="hero-motivation">{motivation_msg}</p>
        <div class="hero-meta-row">
          <span class="hero-date">📅 {today_str}</span>
          <span class="hero-meta-divider">|</span>
          <span class="hero-trend">📈 Trend: {trend_str}</span>
          <span class="hero-meta-divider">|</span>
          <span class="hero-semester">Semester: Spring 2026</span>
        </div>
      </div>
      <div class="hero-right">
        <div class="circular-progress-container">
          <svg class="progress-ring" width="120" height="120">
            <circle class="progress-ring-track" cx="60" cy="60" r="50" stroke="rgba(255, 255, 255, 0.2)" stroke-width="8" fill="transparent" />
            <circle class="progress-ring-fill" id="hero-progress-ring-fill" cx="60" cy="60" r="50" stroke="#FFFFFF" stroke-width="8" fill="transparent"
                    stroke-dasharray="314.159" stroke-dashoffset="314.159" stroke-linecap="round" />
          </svg>
          <div class="progress-text-container">
            <span class="progress-pct-value" id="hero-pct-counter" data-target="{pct_all}">0%</span>
          </div>
        </div>
        <span class="status-badge-hero {status_class}">{status_label}</span>
      </div>
    </div>
  </div>

</div>
""", unsafe_allow_html=True)

    # SECTION 2: QUICK ACTIONS
    q1, q2, q3, q4 = st.columns(4, gap="medium")
    with q1:
        st.markdown("""
        <a href="#subject-performance" target="_self" style="text-decoration: none;">
          <div class="action-card">
            <div class="action-icon">📋</div>
            <div class="action-title">View Attendance</div>
            <div class="action-sub">Check your subject-wise logs</div>
          </div>
        </a>
        """, unsafe_allow_html=True)
    with q2:
        st.markdown("""
        <a href="#attendance-analytics" target="_self" style="text-decoration: none;">
          <div class="action-card">
            <div class="action-icon">📈</div>
            <div class="action-title">Attendance Analytics</div>
            <div class="action-sub">Analyze semester charts</div>
          </div>
        </a>
        """, unsafe_allow_html=True)
    with q3:
        st.markdown("""
        <a href="#subject-performance" target="_self" style="text-decoration: none;">
          <div class="action-card">
            <div class="action-icon">📚</div>
            <div class="action-title">View Subjects</div>
            <div class="action-sub">View all enrolled courses</div>
          </div>
        </a>
        """, unsafe_allow_html=True)
    with q4:
        # Prepare CSV data for download
        import pandas as pd
        report_rows = []
        for log in logs:
            sid = log.get("subject_id")
            sinfo = subjects_map.get(sid, {})
            sname = sinfo.get("name", "Unknown")
            scode = sinfo.get("subject_code", "N/A")
            sec_lbl = sinfo.get("section", "N/A")
            present = "Present" if log.get("is_present") else "Absent"
            ts = log.get("timestamp", "")
            report_rows.append({
                "Subject": sname,
                "Code": scode,
                "Section": sec_lbl,
                "Status": present,
                "Timestamp": ts
            })
        df_report = pd.DataFrame(report_rows)
        csv_data = df_report.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="📥 Download CSV Report",
            data=csv_data,
            file_name=f"Attendance_Report_{name}.csv",
            mime="text/csv",
            use_container_width=True,
            key="action_download"
        )

    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

    # SECTION 3: KPI METRICS GRID
    k1, k2, k3, k4 = st.columns(4, gap="medium")
    with k1:
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-icon-container">📚</div>
          <div class="kpi-value" id="kpi-subjects-counter" data-target="{len(subjects)}">0</div>
          <div class="kpi-label">Subjects Enrolled</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-icon-container">📅</div>
          <div class="kpi-value" id="kpi-total-counter" data-target="{total_all}">0</div>
          <div class="kpi-label">Total Classes</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-icon-container">✅</div>
          <div class="kpi-value" id="kpi-attended-counter" data-target="{attended_all}">0</div>
          <div class="kpi-label">Classes Attended</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-icon-container">📊</div>
          <div class="kpi-value" id="kpi-pct-counter" data-target="{pct_all}" style="color: {trend_color};">0%</div>
          <div class="kpi-label">Overall Attendance</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

    # SECTION 4: ATTENDANCE ANALYTICS (HTML/CSS Bar Chart)
    chart_html = _render_html_bar_chart(stats_map, subjects_map, pct_all)
    st.markdown(chart_html, unsafe_allow_html=True)

    # SECTION 5: ATTENDANCE INSIGHTS
    if total_all > 0:
        classes_can_miss = max(0, math.floor(attended_all / 0.75 - total_all)) if pct_all >= 75 else 0
        classes_to_85 = max(0, math.ceil((0.85 * total_all - attended_all) / 0.15))
    else:
        classes_can_miss = 0
        classes_to_85 = 0

    st.markdown(f"""
    <div class="kpi-card" style="margin-bottom: 24px;" id="attendance-insights">
      <h3 style="font-size: 16px; font-weight: 600; color: var(--text-primary); margin: 0 0 16px 0;">Attendance Insights</h3>
      <div class="insights-grid">
        <div class="insight-tile hover-lift">
          <div class="insight-header">
            <span class="insight-icon" style="color: {trend_color};">📊</span>
            <span class="insight-label">Overall Attendance</span>
          </div>
          <div class="insight-val" style="color: {trend_color};">{pct_all:.1f}%</div>
          <div class="insight-desc">Calculated across all registered subjects.</div>
        </div>
        <div class="insight-tile hover-lift">
          <div class="insight-header">
            <span class="insight-icon" style="color: #6366F1;">🛡️</span>
            <span class="insight-label">Classes You Can Miss</span>
          </div>
          <div class="insight-val" style="color: var(--text-primary);">{classes_can_miss}</div>
          <div class="insight-desc">Without dropping below the 75% requirement.</div>
        </div>
        <div class="insight-tile hover-lift">
          <div class="insight-header">
            <span class="insight-icon" style="color: #6366F1;">🎯</span>
            <span class="insight-label">Classes Needed for 85%</span>
          </div>
          <div class="insight-val" style="color: var(--text-primary);">{classes_to_85}</div>
          <div class="insight-desc">Required to enter the safe zone.</div>
        </div>
        <div class="insight-tile hover-lift">
          <div class="insight-header">
            <span class="insight-icon" style="color: {trend_color};">{trend_arrow}</span>
            <span class="insight-label">Attendance Momentum</span>
          </div>
          <div class="insight-val" style="color: {trend_color};">{trend_str}</div>
          <div class="insight-desc">Compared to your past attendance rate.</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # SECTION 6: SUBJECT PERFORMANCE GRID
    st.markdown("""
    <div id="subject-performance" style="margin-bottom: 12px;">
      <h3 style="font-size: 16px; font-weight: 600; color: var(--text-primary); margin: 0;">Subject Performance</h3>
      <p style="font-size: 13px; color: var(--text-secondary); margin: 2px 0 16px 0;">Your registered subjects and performance status</p>
    </div>
    """, unsafe_allow_html=True)

    if not subjects:
        st.markdown("""
        <div class="empty-state-container">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="empty-state-svg">
            <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"></path>
            <path d="M6 6h10"></path>
            <path d="M6 10h10"></path>
            <path d="M12 14h2"></path>
            <circle cx="12" cy="14" r="3" fill="#EEF2FF" stroke="var(--primary-color)"></circle>
            <line x1="12" y1="12" x2="12" y2="16"></line>
            <line x1="10" y1="14" x2="14" y2="14"></line>
          </svg>
          <h4 class="empty-state-title">No subjects yet</h4>
          <p class="empty-state-subtitle">Your subjects will appear here once enrolled. Click "＋ Enroll" to get started.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        chunk_size = 3
        for chunk_idx in range(0, len(subjects), chunk_size):
            chunk = subjects[chunk_idx : chunk_idx + chunk_size]
            cols = st.columns(3, gap="medium")
            for i, sn in enumerate(chunk):
                with cols[i]:
                    sub  = sn.get("subjects", {})
                    sid  = sub.get("subject_id")
                    stat = stats_map.get(sid, {"total": 0, "attended": 0})
                    att  = stat["attended"]
                    tot  = stat["total"]
                    pct  = int(att / tot * 100) if tot > 0 else 0
                    
                    teacher_name = teachers_map.get(sub.get("teacher_id"), "Professor N/A")
                    
                    if pct >= 85:
                        card_class = "safe"
                        card_status = "Safe"
                    elif pct >= 75:
                        card_class = "warning"
                        card_status = "Warning"
                    else:
                        card_class = "critical"
                        card_status = "Critical"
                        
                    st.markdown(f"""
                    <div class="subject-card {card_class}">
                      <div class="subject-header">
                        <span class="subject-title">{sub.get("name", "—")}</span>
                        <span class="status-badge-small {card_class}">{card_status}</span>
                      </div>
                      <div class="subject-body">
                        <div class="subject-meta">👤 {teacher_name}</div>
                        <div class="subject-meta">Section: {sub.get("section", "—")} · Code: {sub.get("subject_code", "—")}</div>
                        <div class="card-divider"></div>
                        <div class="progress-label-row">
                          <span class="label">Attendance</span>
                          <span class="pct-val {card_class}">{pct}%</span>
                        </div>
                        <div class="progress-bar-track">
                          <div class="progress-bar-fill {card_class}" style="width: {pct}%; --target-width: {pct}%;"></div>
                        </div>
                        
                        <div class="subject-footer-stats">
                          <div class="footer-stat-col">
                            <span class="stat-num">{tot}</span>
                            <span class="stat-lbl">Total</span>
                          </div>
                          <div class="footer-stat-col">
                            <span class="stat-num">{att}</span>
                            <span class="stat-lbl">Attended</span>
                          </div>
                          <div class="footer-stat-col">
                            <span class="stat-num {'text-red' if (tot - att) > 0.15*tot else ''}">{tot - att}</span>
                            <span class="stat-lbl">Missed</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("Unenroll", type="tertiary", use_container_width=True, icon=":material/delete_forever:", key=f"unenroll_{sid}"):
                        unenroll_student_to_subject(student_id, sid)
                        st.toast(f"Unenrolled from {sub.get('name','')}")
                        st.rerun()

    # SECTION 7: RECENT ACTIVITY TIMELINE
    recent = sorted(logs, key=lambda x: x.get("timestamp", ""), reverse=True)[:10]
    
    timeline_items = ""
    for idx, log in enumerate(recent):
        present = log.get("is_present", False)
        ts_raw = log.get("timestamp", "")
        try:
            ts = datetime.fromisoformat(ts_raw).strftime("%d %b %Y · %I:%M %p")
        except Exception:
            ts = ts_raw[:16] if ts_raw else "—"
            
        sid = log.get("subject_id")
        sinfo = subjects_map.get(sid, {})
        sname = sinfo.get("name", "Unknown")
        scode = sinfo.get("subject_code", "N/A")
        
        if present:
            status_class = "present"
            status_label = "Present"
            sym = "✓"
        else:
            status_class = "absent"
            status_label = "Absent"
            sym = "✗"
            
        delay = idx * 50
        timeline_items += f"""
        <div class="timeline-row animate-timeline-item" style="animation-delay: {delay}ms;">
          <div class="timeline-left">
            <div class="timeline-dot {status_class}">{sym}</div>
            <div class="timeline-line"></div>
          </div>
          <div class="timeline-content">
            <div class="timeline-title-row">
              <span class="timeline-subject">{sname}</span>
              <span class="status-pill {status_class}">{status_label}</span>
            </div>
            <div class="timeline-meta">Code: {scode} · {ts}</div>
          </div>
        </div>
        """

    st.markdown(f"""
    <div class="kpi-card" style="margin-top: 10px; margin-bottom: 24px;">
      <h3 style="font-size: 16px; font-weight: 600; color: var(--text-primary); margin: 0 0 16px 0;">Recent Activity Timeline</h3>
      <div class="timeline-container">
        {timeline_items if timeline_items else '<div class="empty-timeline">📅<br><b>No recent activity</b><br><span style="font-size:12px; color:var(--text-secondary);">Your attendance history is currently empty.</span></div>'}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # SECTION 8: FOOTER SUMMARY
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if pct_all >= 85:
        footer_msg = "Outstanding! Keep maintaining this standard."
    elif pct_all >= 75:
        footer_msg = "Good job! Stay consistent to keep your status safe."
    else:
        footer_msg = "Take action. Reach out to your instructors and prioritize attending the next sessions."

    st.markdown(f"""
    <div style="border-top: 1px solid var(--border-color); padding-top: 16px; margin-top: 32px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
      <div>
        <span style="font-size: 12px; color: var(--text-secondary);">Current Status: </span>
        <span class="status-badge-small {status_class}" style="display: inline-block;">{status_label}</span>
        <span style="font-size: 12px; color: var(--text-secondary); margin-left: 8px;">{footer_msg}</span>
      </div>
      <div style="font-size: 11px; color: var(--text-hint);">
        Last synced: {now_str} (Local Time)
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Injected Javascript for Counter and Progress animations
    st.markdown("""
<script>
(function() {
  const root = document.getElementById("student-dashboard-root");
  if (root && !root.getAttribute("data-animated")) {
    root.setAttribute("data-animated", "true");

    // Value counter animation
    function animateValue(id, duration) {
      const obj = document.getElementById(id);
      if (!obj) return;
      const end = parseFloat(obj.getAttribute("data-target"));
      if (isNaN(end) || end === 0) {
        obj.innerText = "0" + (id.includes("pct") ? "%" : "");
        return;
      }
      const isPercent = id.includes("pct");
      let start = 0;
      let current = start;
      const range = end - start;
      const stepTime = Math.max(10, Math.floor(duration / range));
      const timer = setInterval(() => {
        current += 1;
        if (current >= end) {
          obj.innerText = end + (isPercent ? "%" : "");
          clearInterval(timer);
        } else {
          obj.innerText = current + (isPercent ? "%" : "");
        }
      }, stepTime);
    }

    // Run animations
    setTimeout(() => {
      animateValue("hero-pct-counter", 1000);
      animateValue("kpi-subjects-counter", 1000);
      animateValue("kpi-total-counter", 1000);
      animateValue("kpi-attended-counter", 1000);
      animateValue("kpi-pct-counter", 1000);

      // SVG circular progress fill animation
      const fillCircle = document.getElementById("hero-progress-ring-fill");
      if (fillCircle) {
        const pctObj = document.getElementById("hero-pct-counter");
        if (pctObj) {
          const targetPct = parseFloat(pctObj.getAttribute("data-target")) || 0;
          const targetOffset = 314.159 * (1 - targetPct / 100);
          fillCircle.style.strokeDashoffset = targetOffset;
        }
      }
    }, 100);
  }
})();
</script>
""", unsafe_allow_html=True)

    footer_dashboard()


# ════════════════════════════════════════════════════════════════════════════
# LOGIN  — split layout
# ════════════════════════════════════════════════════════════════════════════
def student_screen():
    style_background_dashboard()
    style_base_layout()

    if "student_data" in st.session_state:
        student_dashboard()
        return

    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
.sal{{background:linear-gradient(145deg,#6366F1 0%,#818CF8 60%,#6366F1 100%);
  border-radius:20px;padding:3rem 2.5rem;display:flex;flex-direction:column;
  justify-content:center;min-height:540px;}}
.sal h2{{font-size:1.55rem!important;font-weight:900!important;color:#fff!important;
  letter-spacing:-0.04em!important;margin-bottom:0.75rem!important;
  font-family:'Inter',sans-serif!important;}}
.sal p{{font-size:0.87rem!important;color:rgba(255,255,255,0.72)!important;
  line-height:1.65!important;margin-bottom:1.75rem!important;
  font-family:'Inter',sans-serif!important;}}
.sal ul{{list-style:none;padding:0;margin:0;}}
.sal li{{font-size:0.81rem;color:rgba(255,255,255,0.85);font-family:'Inter',sans-serif;
  margin-bottom:10px;display:flex;align-items:center;gap:10px;}}
.sal-ck{{width:20px;height:20px;border-radius:50%;background:rgba(255,255,255,0.18);
  display:flex;align-items:center;justify-content:center;font-size:0.62rem;
  color:#fff;flex-shrink:0;}}
.sar{{background:#fff;border:1px solid #E2E8F0;border-radius:20px;padding:2.25rem 2rem;}}
.sar-logo{{display:flex;align-items:center;gap:10px;margin-bottom:1.5rem;}}
.sar-logo .wm{{font-family:'Inter',sans-serif;font-size:1rem;font-weight:800;
  color:#6366F1;letter-spacing:-0.03em;}}
</style>
""", unsafe_allow_html=True)

    bc, _ = st.columns([1, 4])
    with bc:
        if st.button("← Home", type="secondary"):
            st.session_state["login_type"] = None
            st.rerun()
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    lc, rc = st.columns([1, 1.1], gap="large")

    with lc:
        st.markdown(f"""
<div class="sal">
  <div style="margin-bottom:1.5rem;">{_LOGO}</div>
  <h2>Student Login</h2>
  <p>Sign in with Face ID instantly — no password, no typing. Just look at the camera.</p>
  <ul>
    <li><span class="sal-ck">✓</span> Instant AI face recognition login</li>
    <li><span class="sal-ck">✓</span> View attendance across all subjects</li>
    <li><span class="sal-ck">✓</span> Track your attendance percentage live</li>
    <li><span class="sal-ck">✓</span> Join subjects via QR code</li>
    <li><span class="sal-ck">✓</span> Attendance trend charts and history</li>
  </ul>
</div>""", unsafe_allow_html=True)

    with rc:
        st.markdown(f"""
<div class="sar">
  <div class="sar-logo">{_LOGO}<span class="wm">SmartAttend</span></div>
  <div style="font-size:1.2rem;font-weight:800;color:#0F172A;letter-spacing:-0.03em;
       font-family:'Inter',sans-serif;margin-bottom:4px;">Sign in with Face ID</div>
  <div style="font-size:0.82rem;color:#64748B;font-family:'Inter',sans-serif;
       margin-bottom:1.25rem;">Position your face in the camera frame below.</div>
""", unsafe_allow_html=True)

        show_reg = False
        photo = st.camera_input("Look directly at the camera")

        if photo:
            img = np.array(Image.open(photo))
            with st.spinner("Scanning with AI…"):
                detected, _, num_faces = predict_attendance(img)
                if num_faces == 0:
                    st.warning("No face detected. Move closer and ensure good lighting.")
                elif num_faces > 1:
                    st.warning("Multiple faces detected. Only one person should be in frame.")
                else:
                    if detected:
                        sid_key = list(detected.keys())[0]
                        all_st  = get_all_students()
                        student = next(
                            (s for s in all_st if s["student_id"] == sid_key), None
                        )
                        if student:
                            st.session_state.is_logged_in = True
                            st.session_state.user_role    = "student"
                            st.session_state.student_data = student
                            st.toast(f"Welcome back, {student['name']}! 👋")
                            time.sleep(0.8)
                            st.rerun()
                    else:
                        st.info("Face not recognised. Register below if you are new.")
                        show_reg = True

        st.markdown("</div>", unsafe_allow_html=True)

        if show_reg:
            st.markdown("""
<div style="background:#F5F3FF;border:1px solid #DDD6FE;border-radius:14px;
     padding:1.5rem 1.75rem;margin-top:1rem;">
  <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
       letter-spacing:0.08em;color:#7C3AED;margin-bottom:1rem;
       font-family:'Inter',sans-serif;">✨ New Student — Create Profile</div>
""", unsafe_allow_html=True)
            new_name = st.text_input("Full Name", placeholder="e.g. Priya Sharma")
            audio_data = None
            try:
                audio_data = st.audio_input("Optional: record your voice for voice-based attendance")
            except Exception:
                pass
            if st.button("Create Account →", type="primary", use_container_width=True):
                if new_name:
                    with st.spinner("Setting up your profile…"):
                        encodings = get_face_embeddings(np.array(Image.open(photo)))
                        if encodings:
                            face_emb  = encodings[0].tolist()
                            voice_emb = None
                            if audio_data:
                                voice_emb = get_voice_embedding(audio_data.read())
                            resp = create_student(
                                new_name,
                                face_embedding=face_emb,
                                voice_embedding=voice_emb,
                            )
                            if resp:
                                train_classifier()
                                st.session_state.is_logged_in = True
                                st.session_state.user_role    = "student"
                                st.session_state.student_data = resp[0]
                                st.toast(f"Welcome, {new_name}! 🎉")
                                time.sleep(0.8)
                                st.rerun()
                        else:
                            st.error("Could not capture face features. Retake photo.")
                else:
                    st.warning("Please enter your full name.")
            st.markdown("</div>", unsafe_allow_html=True)

    footer_dashboard()
