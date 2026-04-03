import streamlit as st
from utils.ui import page_header, GOLD
from data.catalog import GIN_LIST

def show():
    page_header("The Gin Bar", "La collezione di gin con botaniche e abbinamenti", "🍸")

    search = st.text_input("🔍 Cerca gin", placeholder="Hendrick's, Sicilia, Bergamo…", label_visibility="collapsed")

    filtered = GIN_LIST
    if search:
        s = search.lower()
        filtered = [g for g in filtered
                    if s in g["name"].lower()
                    or s in g.get("origin","").lower()
                    or s in " ".join(g.get("botanicals",[])).lower()
                    or s in g.get("distillery","").lower()]

    st.markdown(f"<div style='color:#888;font-size:.8rem;margin-bottom:1rem;'>{len(filtered)} gin trovati</div>", unsafe_allow_html=True)

    cols = st.columns(2)
    for i, gin in enumerate(filtered):
        color     = gin.get("color","#2D5A3A")
        emoji     = gin.get("emoji","🍸")
        botanicals= gin.get("botanicals",[])
        garnish   = gin.get("garnish","—")

        bot_html = " ".join(
            f'<span style="background:{color}22;color:{color};border:1px solid {color}44;'
            f'border-radius:99px;padding:2px 8px;font-size:.7rem;">{b}</span>'
            for b in botanicals
        )

        with cols[i % 2]:
            st.markdown(f"""
            <div style="background:#1A1A1A;border:1px solid {color}44;border-radius:14px;
                        padding:1.25rem;margin-bottom:1rem;">
              <div style="display:flex;align-items:flex-start;gap:.75rem;margin-bottom:.8rem;">
                <div style="font-size:2rem;">{emoji}</div>
                <div style="flex:1;">
                  <div style="font-size:1.1rem;font-weight:800;color:{color};">{gin['name']}</div>
                  <div style="font-size:.75rem;color:#888;">{gin.get('distillery','')} · {gin.get('origin','')}</div>
                </div>
              </div>
              <p style="color:#aaa;font-size:.82rem;line-height:1.6;margin-bottom:.75rem;">
                {gin.get('description','')}
              </p>
              <div style="font-size:.65rem;color:#666;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.4rem;">
                🌿 Botaniche
              </div>
              <div style="margin-bottom:.75rem;">{bot_html}</div>
              <div style="background:#111;border-radius:8px;padding:.6rem;">
                <span style="font-size:.65rem;color:#666;text-transform:uppercase;">🍋 Garnish perfetto: </span>
                <span style="font-size:.82rem;color:{GOLD};font-weight:600;">{garnish}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)
