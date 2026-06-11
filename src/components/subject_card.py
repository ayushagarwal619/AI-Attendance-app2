import streamlit as st


def subject_card(name, code, section, stats=None, footer_callback=None):
    """
    Premium subject card.
    stats: list of (icon, label, value) tuples.
    If a stat with label 'Attendance' or ending in '%' is found, renders a progress bar.
    """
    # Extract attendance % for progress bar if present
    pct_val = None
    for (icon, label, value) in (stats or []):
        if label.lower() in ("attendance", "attendance %") or (isinstance(value, str) and value.endswith("%")):
            try:
                pct_val = int(str(value).replace("%", "").strip())
            except ValueError:
                pass

    # Progress bar colour
    if pct_val is not None:
        if pct_val >= 75:
            bar_color = "#10B981"   # green
        elif pct_val >= 50:
            bar_color = "#F59E0B"   # amber
        else:
            bar_color = "#EF4444"   # red
        bar_pct = min(pct_val, 100)
    else:
        bar_color = "#4F46E5"
        bar_pct = 0

    # Build stat chips HTML
    chips_html = ""
    if stats:
        chips_html = '<div style="display:flex; gap:6px; flex-wrap:wrap; margin:12px 0 0;">'
        for icon, label, value in stats:
            chips_html += f"""
            <div style="display:flex; align-items:center; gap:4px; background:#F9FAFB;
                        border:1px solid #E5E7EB; padding:4px 10px; border-radius:6px;
                        font-size:0.78rem; color:#374151; font-family:'Inter',sans-serif;">
              <span>{icon}</span>
              <span style="font-weight:600; color:#111827;">{value}</span>
              <span style="color:#6B7280;">{label}</span>
            </div>"""
        chips_html += "</div>"

    progress_html = ""
    if pct_val is not None:
        progress_html = f"""
        <div style="margin-top:14px;">
          <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
            <span style="font-size:0.72rem; font-weight:500; color:#6B7280;
                         font-family:'Inter',sans-serif; text-transform:uppercase; letter-spacing:0.05em;">
              Attendance
            </span>
            <span style="font-size:0.72rem; font-weight:700; color:{bar_color};
                         font-family:'Inter',sans-serif;">{pct_val}%</span>
          </div>
          <div style="height:5px; background:#F3F4F6; border-radius:100px; overflow:hidden;">
            <div style="height:100%; width:{bar_pct}%; background:{bar_color};
                        border-radius:100px; transition:width 0.4s ease;"></div>
          </div>
        </div>"""

    card_html = f"""
    <style>
    .sa-subject-card {{
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 20px 22px;
        margin-bottom: 14px;
        position: relative;
        overflow: hidden;
        transition: box-shadow 0.2s ease, transform 0.2s ease;
    }}
    .sa-subject-card::before {{
        content: '';
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 4px;
        background: linear-gradient(180deg, #4F46E5, #7C3AED);
        border-radius: 4px 0 0 4px;
    }}
    </style>
    <div class="sa-subject-card">
      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:4px;">
        <h3 style="margin:0; font-size:1rem; font-weight:700; color:#111827;
                   font-family:'Inter',sans-serif; letter-spacing:-0.01em;">{name}</h3>
        <span style="font-size:0.72rem; font-weight:600; background:#EEF2FF; color:#4F46E5;
                     padding:3px 9px; border-radius:100px; white-space:nowrap;
                     font-family:'Inter',sans-serif;">{code}</span>
      </div>
      <p style="font-size:0.8rem; color:#6B7280; margin:2px 0 0;
                font-family:'Inter',sans-serif;">Section &nbsp;<b style="color:#374151;">{section}</b></p>
      {chips_html}
      {progress_html}
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)

    if footer_callback:
        footer_callback()
