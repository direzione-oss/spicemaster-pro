import streamlit as st
from utils.ui import page_header, GOLD
from data.catalog import GIN_LIST

def show():
    page_header("The Gin Bar", f"Collezione di {len(GIN_LIST)} gin con botaniche e abbinamenti", "🍸")

    col1, col2 = st.columns([3, 2])
    with col1:
        search = st.text_input("🔍 Cerca gin", placeholder="Hendrick's, Sicilia, Bergamo, yuzu…", label_visibility="collapsed", key="gin_search")
    with col2:
        origins = ["Tutte le origini"] + sorted(set(g.get("origin","").split(",")[-1].strip() for g in GIN_LIST if g.get("origin","")))
        origin_filter = st.selectbox("Origine", origins, label_visibility="collapsed", key="gin_origin")

    filtered = GIN_LIST
    if search:
        s = search.lower()
        filtered = [g for g in filtered if
                    s in g["name"].lower() or
                    s in g.get("origin","").lower() or
                    s in g.get("description","").lower() or
                    s in " ".join(g.get("botanicals",[])).lower()]
    if origin_filter != "Tutte le origini":
        filtered = [g for g in filtered if origin_filter in g.get("origin","")]

    st.markdown(f"<div style='color:#888;font-size:.8rem;margin-bottom:1rem;'>{len(filtered)} gin trovati</div>", unsafe_allow_html=True)

    cols = st.columns(2)
    for i, gin in enumerate(filtered):
        color     = gin.get("color","#2D5A3A")
        botanicals = gin.get("botanicals",[])
        serve     = gin.get("serve","—")

        bot_html = " ".join(
            f'<span style="background:{color}22;color:{color};border:1px solid {color}44;'
            f'border-radius:99px;padding:2px 9px;font-size:.7rem;">{b}</span>'
            for b in botanicals
        )

        with cols[i % 2]:
            st.markdown(f"""
            <div style="background:#1A1A1A;border:1px solid {color}55;border-radius:14px;
                        padding:1.25rem;margin-bottom:1rem;">
              <div style="display:flex;align-items:center;gap:.75rem;margin-bottom:.75rem;">
                <div style="width:42px;height:42px;background:{color};border-radius:10px;
                            display:flex;align-items:center;justify-content:center;font-size:1.4rem;">🍸</div>
                <div style="flex:1;">
                  <div style="font-size:1.05rem;font-weight:800;color:{color};">{gin['name']}</div>
                  <div style="font-size:.73rem;color:#888;">📍 {gin.get('origin','')}</div>
                </div>
              </div>
              <p style="color:#aaa;font-size:.82rem;line-height:1.65;margin-bottom:.8rem;">
                {gin.get('description','')}
              </p>
              <div style="font-size:.62rem;color:#555;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.4rem;">
                🌿 Botaniche
              </div>
              <div style="margin-bottom:.85rem;line-height:1.8;">{bot_html}</div>
              <div style="background:#111;border-radius:8px;padding:.65rem;">
                <span style="font-size:.62rem;color:#555;text-transform:uppercase;letter-spacing:.08em;">🍋 Come servirlo: </span>
                <div style="font-size:.82rem;color:{GOLD};font-weight:600;margin-top:.2rem;">{serve}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
