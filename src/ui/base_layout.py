import streamlit as st


# ─── Design Tokens ────────────────────────────────────────────────────────────
PRIMARY   = "#4F46E5"
SECONDARY = "#7C3AED"
ACCENT    = "#06B6D4"
SUCCESS   = "#10B981"
WARNING   = "#F59E0B"
DANGER    = "#EF4444"
GRAY_50   = "#F9FAFB"
GRAY_100  = "#F3F4F6"
GRAY_200  = "#E5E7EB"
GRAY_300  = "#D1D5DB"
GRAY_400  = "#9CA3AF"
GRAY_600  = "#4B5563"
GRAY_700  = "#374151"
GRAY_800  = "#1F2937"
GRAY_900  = "#111827"
WHITE     = "#FFFFFF"


def render_theme_toggle():
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False
    label = "☀️ Light" if st.session_state.dark_mode else "🌙 Dark"
    if st.button(label, key="theme_toggle_btn", type="tertiary"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()


def _dark():
    return st.session_state.get("dark_mode", False)


# ─── Global CSS (injected once per page) ──────────────────────────────────────
def style_base_layout():
    dark = _dark()
    bg        = "#0F0F1A" if dark else GRAY_50
    surface   = "#1A1A2E" if dark else WHITE
    border    = "#2D2D44" if dark else GRAY_200
    text_main = "#F1F5F9" if dark else GRAY_900
    text_muted= "#94A3B8" if dark else GRAY_600
    input_bg  = "#1E1E30" if dark else WHITE

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Reset & Root ── */
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }}

    /* ── App Shell ── */
    .stApp {{
        background: {bg} !important;
        color: {text_main} !important;
    }}

    /* ── Remove Streamlit chrome ── */
    #MainMenu, footer, header {{ visibility: hidden !important; }}
    .stDeployButton {{ display: none !important; }}

    /* ── Block container ── */
    .block-container {{
        padding: 1.5rem 2rem 3rem !important;
        max-width: 1280px !important;
        margin: 0 auto !important;
    }}

    /* ── Typography ── */
    h1 {{
        font-family: 'Inter', sans-serif !important;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.04em !important;
        line-height: 1.1 !important;
        color: {text_main} !important;
    }}
    h2 {{
        font-family: 'Inter', sans-serif !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
        color: {text_main} !important;
    }}
    h3 {{
        font-family: 'Inter', sans-serif !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: {text_main} !important;
    }}
    p, label, .stMarkdown, .stText {{
        font-family: 'Inter', sans-serif !important;
        color: {text_muted} !important;
        font-size: 0.9rem !important;
    }}

    /* ── Inputs ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {{
        background: {input_bg} !important;
        border: 1px solid {border} !important;
        border-radius: 8px !important;
        color: {text_main} !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.9rem !important;
        padding: 0.6rem 0.75rem !important;
        transition: border-color 0.2s ease !important;
    }}
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {PRIMARY} !important;
        box-shadow: 0 0 0 3px rgba(79,70,229,0.15) !important;
    }}

    /* ── Buttons ── */
    button[kind="primaryFormSubmit"],
    button[kind="primary"] {{
        background: {PRIMARY} !important;
        color: {WHITE} !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        padding: 0.55rem 1.25rem !important;
        transition: background 0.2s ease, transform 0.15s ease, box-shadow 0.15s ease !important;
        box-shadow: 0 1px 3px rgba(79,70,229,0.3) !important;
    }}
    button[kind="primary"]:hover {{
        background: #4338CA !important;
        box-shadow: 0 4px 12px rgba(79,70,229,0.4) !important;
        transform: translateY(-1px) !important;
    }}
    button[kind="secondary"] {{
        background: transparent !important;
        color: {text_main} !important;
        border: 1px solid {border} !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        padding: 0.55rem 1.25rem !important;
        transition: background 0.2s ease, border-color 0.2s ease !important;
    }}
    button[kind="secondary"]:hover {{
        background: {GRAY_100} !important;
        border-color: {GRAY_300} !important;
    }}
    button[kind="tertiary"] {{
        background: transparent !important;
        color: {PRIMARY} !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        padding: 0.55rem 1rem !important;
        transition: background 0.2s ease !important;
    }}
    button[kind="tertiary"]:hover {{
        background: rgba(79,70,229,0.08) !important;
    }}

    /* ── Metrics ── */
    [data-testid="stMetric"] {{
        background: {surface} !important;
        border: 1px solid {border} !important;
        border-radius: 12px !important;
        padding: 1.25rem 1.5rem !important;
    }}
    [data-testid="stMetricLabel"] {{
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: {text_muted} !important;
    }}
    [data-testid="stMetricValue"] {{
        font-size: 1.75rem !important;
        font-weight: 800 !important;
        color: {text_main} !important;
        letter-spacing: -0.03em !important;
    }}

    /* ── Dividers ── */
    hr {{
        border: none !important;
        border-top: 1px solid {border} !important;
        margin: 1.5rem 0 !important;
    }}

    /* ── Dataframes ── */
    [data-testid="stDataFrame"] {{
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid {border} !important;
    }}

    /* ── Spinner ── */
    .stSpinner > div {{ border-top-color: {PRIMARY} !important; }}

    /* ── Toast ── */
    [data-testid="stToast"] {{
        border-radius: 10px !important;
        font-family: 'Inter', sans-serif !important;
    }}

    /* ── Select box ── */
    [data-testid="stSelectbox"] label {{
        font-weight: 500 !important;
        color: {text_main} !important;
    }}

    /* ── Responsive ── */
    @media (max-width: 768px) {{
        h1 {{ font-size: 1.8rem !important; }}
        h2 {{ font-size: 1.2rem !important; }}
        .block-container {{ padding: 1rem !important; }}
    }}
    </style>
    """, unsafe_allow_html=True)


def style_background_home():
    st.markdown("""
    <style>
    .stApp { background: #F9FAFB !important; }
    </style>
    """, unsafe_allow_html=True)


def style_background_dashboard():
    dark = _dark()
    bg = "#0F0F1A" if dark else GRAY_50
    st.markdown(f"""
    <style>
    .stApp {{ background: {bg} !important; }}
    </style>
    """, unsafe_allow_html=True)
