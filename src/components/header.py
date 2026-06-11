import streamlit as st


# ── Inline SVG logo mark ──────────────────────────────────────────────────────
_LOGO_SVG = """
<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="32" height="32" rx="8" fill="#4F46E5"/>
  <path d="M8 10h10M8 16h16M8 22h12" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
  <circle cx="24" cy="10" r="3" fill="#06B6D4"/>
</svg>"""


def header_home():
    """Minimal top navbar for the landing page."""
    st.markdown(f"""
    <style>
    .sa-nav {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 0;
        border-bottom: 1px solid #E5E7EB;
        margin-bottom: 0;
    }}
    .sa-nav-brand {{
        display: flex;
        align-items: center;
        gap: 10px;
        text-decoration: none;
    }}
    .sa-nav-brand span {{
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        font-weight: 800;
        color: #111827;
        letter-spacing: -0.03em;
    }}
    .sa-nav-tag {{
        font-size: 0.7rem;
        font-weight: 600;
        background: #EEF2FF;
        color: #4F46E5;
        padding: 2px 8px;
        border-radius: 100px;
        letter-spacing: 0.03em;
    }}
    </style>
    <div class="sa-nav">
      <div class="sa-nav-brand">
        {_LOGO_SVG}
        <span>SmartAttend</span>
        <span class="sa-nav-tag">BETA</span>
      </div>
    </div>
    """, unsafe_allow_html=True)


def header_dashboard():
    """Compact brand mark used inside dashboards (top-left of the header row)."""
    st.markdown(f"""
    <style>
    .sa-dash-brand {{
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    .sa-dash-brand span {{
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        font-weight: 800;
        color: #4F46E5;
        letter-spacing: -0.03em;
    }}
    </style>
    <div class="sa-dash-brand">
      {_LOGO_SVG}
      <span>SmartAttend</span>
    </div>
    """, unsafe_allow_html=True)
