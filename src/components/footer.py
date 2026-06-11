import streamlit as st


def footer_home():
    st.markdown("""
    <style>
    .sa-footer {
        border-top: 1px solid #E5E7EB;
        padding: 2.5rem 0 1.5rem;
        margin-top: 4rem;
    }
    .sa-footer-grid {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        flex-wrap: wrap;
        gap: 2rem;
        margin-bottom: 2rem;
    }
    .sa-footer-brand span {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        font-weight: 800;
        color: #111827;
        letter-spacing: -0.03em;
        display: block;
        margin-bottom: 6px;
    }
    .sa-footer-brand p {
        font-size: 0.8rem;
        color: #6B7280;
        max-width: 220px;
        line-height: 1.5;
    }
    .sa-footer-links h4 {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #374151;
        margin-bottom: 12px;
    }
    .sa-footer-links a {
        display: block;
        font-size: 0.82rem;
        color: #6B7280;
        text-decoration: none;
        margin-bottom: 8px;
        transition: color 0.15s;
    }
    .sa-footer-links a:hover { color: #4F46E5; }
    .sa-footer-bottom {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top: 1px solid #F3F4F6;
        padding-top: 1.25rem;
        font-size: 0.78rem;
        color: #9CA3AF;
    }
    .sa-footer-badge {
        background: #EEF2FF;
        color: #4F46E5;
        padding: 3px 10px;
        border-radius: 100px;
        font-size: 0.72rem;
        font-weight: 600;
    }
    </style>
    <div class="sa-footer">
      <div class="sa-footer-grid">
        <div class="sa-footer-brand">
          <span>SmartAttend</span>
          <p>AI-powered attendance management for modern educational institutions.</p>
        </div>
        <div class="sa-footer-links">
          <h4>Product</h4>
          <a href="#">Features</a>
          <a href="#">How It Works</a>
          <a href="#">Pricing</a>
        </div>
        <div class="sa-footer-links">
          <h4>Support</h4>
          <a href="#">Documentation</a>
          <a href="#">Contact</a>
          <a href="#">Status</a>
        </div>
        <div class="sa-footer-links">
          <h4>Legal</h4>
          <a href="#">Privacy Policy</a>
          <a href="#">Terms of Service</a>
        </div>
      </div>
      <div class="sa-footer-bottom">
        <span>&copy; 2024 SmartAttend. All rights reserved.</span>
        <span class="sa-footer-badge">v2.0</span>
      </div>
    </div>
    """, unsafe_allow_html=True)


def footer_dashboard():
    st.markdown("""
    <div style="margin-top:3rem; padding-top:1.5rem; border-top:1px solid #E5E7EB;
         display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
      <span style="font-size:0.78rem; color:#9CA3AF; font-family:'Inter',sans-serif;">
        &copy; 2024 SmartAttend
      </span>
      <span style="font-size:0.78rem; color:#9CA3AF; font-family:'Inter',sans-serif;">
        AI-Powered Attendance System
      </span>
    </div>
    """, unsafe_allow_html=True)
