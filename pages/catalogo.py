import streamlit as st
from utils.ui import page_header, spice_badge, GOLD
from data.catalog import SPICES_CATALOG, FLAVOR_TAG_COLORS

def show():
    page_header("Catalogo Spezie", f"{len(SPICES_CATALOG)} spezie e botaniche con profilo aromatico completo", "📚")

    # ── Filtri ───────────────────────────────────────────────
    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        search = st.text_input("🔍 Cerca", placeholder="Pepe, Lavanda, Bergamotto…", label_visibility="collapsed")
    with col2:
        categories = ["Tutte"] + sorted(set(s["category"] for s in SPICES_CATALOG))
        cat = st.selectbox("Categoria", categories, label_visibility="collapsed")
    with col3:
        forms = ["Tutte"] + sorted(set(s.get("form","") for s in SPICES_CATALOG if s.get("form","")))
        form_filter = st.selectbox("Forma", forms, label_visibility="collapsed")

    all_tags = sorted(set(t for s in SPICES_CATALOG for t in s.get("tags", [])))
    tag_sel = st.multiselect("🏷️ Filtra per aroma", all_tags)

    # Applica filtri
    filtered = SPICES_CATALOG
    if search:
        s = search.lower()
        filtered = [x for x in filtered if
                    s in x["name"].lower() or
                    s in x.get("botanicalName","").lower() or
                    s in x.get("description","").lower() or
                    s in " ".join(x.get("tags",[])).lower() or
                    s in " ".join(x.get("pairsWith",[])).lower()]
    if cat != "Tutte":
        filtered = [x for x in filtered if x["category"] == cat]
    if form_filter != "Tutte":
        filtered = [x for x in filtered if x.get("form","") == form_filter]
    if tag_sel:
        filtered = [x for x in filtered if any(t in x.get("tags",[]) for t in tag_sel)]

    st.markdown(f"<div style='color:#888;font-size:.8rem;margin-bottom:1rem;'>{len(filtered)} spezie trovate</div>", unsafe_allow_html=True)

    # ── Grid card ────────────────────────────────────────────
    cols = st.columns(3)
    for i, sp in enumerate(filtered):
        color = sp.get("color","#C9900C")
        emoji = sp.get("emoji","🌿")
        tags  = sp.get("tags",[])
        pairs = sp.get("pairsWith",[])

        tags_html = " ".join(
            f'<span style="background:{FLAVOR_TAG_COLORS.get(t,GOLD)}22;color:{FLAVOR_TAG_COLORS.get(t,GOLD)};'
            f'border:1px solid {FLAVOR_TAG_COLORS.get(t,GOLD)}55;'
            f'border-radius:99px;padding:1px 8px;font-size:.65rem;">{t}</span>'
            for t in tags
        )
        pairs_html = " · ".join(f'<span style="color:#aaa;font-size:.78rem;">{p}</span>' for p in pairs[:5])

        with cols[i % 3]:
            with st.expander(f"{emoji} {sp['name']}", expanded=False):
                st.markdown(f"""
                <div style="border-left:3px solid {color};padding-left:.75rem;margin-bottom:.75rem;">
                  <div style="font-style:italic;color:#888;font-size:.75rem;">{sp.get('botanicalName','')}</div>
                  <div style="margin:.3rem 0;">{spice_badge(sp['category'])} &nbsp; <span style="color:#666;font-size:.75rem;">{sp.get('form','')}</span></div>
                </div>
                <div style="font-size:.83rem;color:#aaa;line-height:1.65;margin-bottom:.8rem;">
                  {sp.get('description','')}
                </div>
                <div style="margin-bottom:.6rem;">{tags_html}</div>
                <div style="background:#111;border-radius:8px;padding:.6rem;margin-top:.5rem;">
                  <div style="font-size:.6rem;color:#555;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.3rem;">🍽️ Si abbina con</div>
                  <div>{pairs_html}</div>
                </div>
                """, unsafe_allow_html=True)
