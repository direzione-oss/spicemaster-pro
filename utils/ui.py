import streamlit as st

GOLD  = "#C9900C"
AMBER = "#F4A900"
RED   = "#CC4400"
GREEN = "#5A9A3A"

def page_header(title: str, subtitle: str = "", emoji: str = ""):
    st.markdown(f"""
    <div style="padding:1.5rem 0 1rem; border-bottom:1px solid #C9900C33; margin-bottom:1.5rem;">
      <div style="font-size:0.75rem;color:#888;text-transform:uppercase;letter-spacing:.12em;margin-bottom:.25rem;">
        SpiceMaster Pro
      </div>
      <h1 style="font-size:2rem;color:{GOLD};margin:0;font-weight:800;">
        {emoji + " " if emoji else ""}{title}
      </h1>
      {"<p style='color:#aaa;margin:.25rem 0 0;'>" + subtitle + "</p>" if subtitle else ""}
    </div>
    """, unsafe_allow_html=True)


def metric_card(label: str, value: str, delta: str = "", color: str = GOLD):
    st.markdown(f"""
    <div style="background:#1A1A1A;border:1px solid {color}33;border-radius:12px;
                padding:1.1rem 1.25rem;text-align:center;">
      <div style="font-size:.65rem;color:#888;text-transform:uppercase;letter-spacing:.1em;">{label}</div>
      <div style="font-size:2rem;font-weight:800;color:{color};line-height:1.2;">{value}</div>
      {"<div style='font-size:.75rem;color:#888;margin-top:.15rem;'>" + delta + "</div>" if delta else ""}
    </div>
    """, unsafe_allow_html=True)


def stock_bar(level: int) -> str:
    color = GREEN if level > 60 else (AMBER if level > 25 else RED)
    return f"""
    <div style="background:#222;border-radius:99px;height:8px;overflow:hidden;margin:.3rem 0;">
      <div style="width:{level}%;height:100%;background:{color};border-radius:99px;"></div>
    </div>
    <span style="font-size:.72rem;color:{color};font-weight:600;">{level}%</span>
    """


def spice_badge(category: str) -> str:
    colors = {
        "Spezia": "#C9900C", "Erba": "#5A9A3A", "Botanica": "#6B4A9A",
        "Sale": "#5A8AAF",   "Zucchero": "#C46060",
    }
    c = colors.get(category, "#888")
    return f'<span style="background:{c}22;color:{c};border:1px solid {c}55;border-radius:99px;padding:2px 10px;font-size:.7rem;font-weight:600;">{category}</span>'
