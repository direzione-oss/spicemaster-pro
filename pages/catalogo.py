import streamlit as st
from utils.ui import page_header, spice_badge, GOLD
from data.catalog import SPICES_CATALOG, ALL_CATEGORIES, ALL_FLAVOR_TAGS, ALL_INTENSITIES

def show():
    page_header("Catalogo Spezie", "193 spezie botaniche con profilo aromatico completo", "📚")

    # ── Filtri ───────────────────────────────────────────────
    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        search = st.text_input("🔍 Cerca spezia", placeholder="Pepe, Lavanda, Piperaceae…", label_visibility="collapsed")
    with col2:
        cat = st.selectbox("Categoria", ["Tutte"] + ALL_CATEGORIES, label_visibility="collapsed")
    with col3:
        uso_filter = st.selectbox("Uso", ["Tutti","Cucina","Liquori","Cocktail","Medicina","Tisane","Pasticceria"], label_visibility="collapsed")

    tag_sel = st.multiselect("🏷️ Filtra per tag aromatico", ALL_FLAVOR_TAGS)

    # Applica filtri
    filtered = SPICES_CATALOG
    if search:
        s = search.lower()
        filtered = [x for x in filtered if s in x["name"].lower()
                    or s in x.get("family","").lower()
                    or s in x.get("origin","").lower()
                    or s in " ".join(x.get("tags",[])).lower()]
    if cat != "Tutte":
        filtered = [x for x in filtered if x["category"] == cat]
    if uso_filter != "Tutti":
        filtered = [x for x in filtered if uso_filter in x.get("uses",[])]
    if tag_sel:
        filtered = [x for x in filtered if any(t in x.get("tags",[]) for t in tag_sel)]

    st.markdown(f"<div style='color:#888;font-size:.8rem;margin-bottom:1rem;'>{len(filtered)} spezie trovate</div>", unsafe_allow_html=True)

    # ── Grid card ────────────────────────────────────────────
    USE_ICONS = {"Cucina":"🍳","Pasticceria":"🧁","Cocktail":"🍹","Liquori":"🥃",
                 "Tisane":"🫖","Medicina":"💊","Cosmesi":"💄","Colorante":"🎨",
                 "Profumeria":"🌸","Spirituale":"🕯️"}
    INTENSITY_LABEL = ["","⚪","🟡","🟠","🔴","🔥"]

    cols = st.columns(3)
    for i, sp in enumerate(filtered):
        color     = sp.get("color","#C9900C")
        emoji     = sp.get("emoji","🌿")
        intensity = sp.get("intensity",0)
        uses      = sp.get("uses",[])
        tags      = sp.get("tags",[])
        origin    = sp.get("origin","—")
        family    = sp.get("family","—")

        tags_html = " ".join(
            f'<span style="background:{GOLD}18;color:{GOLD};border:1px solid {GOLD}44;'
            f'border-radius:99px;padding:1px 8px;font-size:.65rem;">{t}</span>'
            for t in tags
        )
        uses_html = " ".join(
            f'<span style="color:#888;font-size:.7rem;">{USE_ICONS.get(u,"")} {u}</span>'
            for u in uses[:3]
        )

        with cols[i % 3]:
            with st.expander(f"{emoji} {sp['name']}", expanded=False):
                st.markdown(f"""
                <div style="border-left:3px solid {color};padding-left:.75rem;margin-bottom:.75rem;">
                  <div style="font-style:italic;color:#888;font-size:.8rem;">{sp.get('botanicalName','')}</div>
                  <div style="margin:.3rem 0;">{spice_badge(sp['category'])}</div>
                </div>
                <div style="font-size:.85rem;color:#aaa;line-height:1.6;margin-bottom:.75rem;">
                  {sp.get('description','')}
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:.5rem;margin-bottom:.75rem;">
                  <div style="background:#111;border-radius:8px;padding:.6rem;">
                    <div style="font-size:.6rem;color:#666;text-transform:uppercase;letter-spacing:.1em;">Origine</div>
                    <div style="font-size:.82rem;color:#E8DCC8;font-weight:600;">{origin}</div>
                  </div>
                  <div style="background:#111;border-radius:8px;padding:.6rem;">
                    <div style="font-size:.6rem;color:#666;text-transform:uppercase;letter-spacing:.1em;">Famiglia</div>
                    <div style="font-size:.82rem;color:#E8DCC8;font-style:italic;">{family}</div>
                  </div>
                </div>
                <div style="margin-bottom:.5rem;">{tags_html}</div>
                <div style="margin-bottom:.5rem;">Intensità: {INTENSITY_LABEL[intensity] * intensity}</div>
                <div>{uses_html}</div>
                """, unsafe_allow_html=True)
