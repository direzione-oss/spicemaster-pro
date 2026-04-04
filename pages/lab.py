import streamlit as st
import math
from utils.ui import page_header, GOLD, GREEN
from data.catalog import SPICES_CATALOG, SPICE_DICT, FLAVOR_TAG_COLORS

# ── Profilo aromatico: pesi per tag ─────────────────────────
TAG_WEIGHTS = {
    "Piccante": 85, "Dolce": 70, "Agrumato": 65, "Affumicato": 80,
    "Legnoso": 60, "Floreale": 55, "Terroso": 70, "Erbaceo": 65,
    "Amaro": 50, "Salato": 40, "Umami": 75, "Fruttato": 60,
}

OPENING = {
    "Piccante":   "Un mix dall'anima ardente e decisa.",
    "Dolce":      "Una miscela avvolgente dalle note morbide e suadenti.",
    "Agrumato":   "Un profilo vivace e fresco, che ricorda i mercati mediterranei.",
    "Affumicato": "Un mix profondo e misterioso, con l'eco del fuoco vivo.",
    "Legnoso":    "Una miscela calda e strutturata, con radici nella terra.",
    "Floreale":   "Un profilo elegante e delicato, quasi profumato.",
    "Terroso":    "Un mix radicato, ricco di complessità minerale.",
    "Erbaceo":    "Una miscela fresca e vitale, con l'essenza del giardino.",
    "Amaro":      "Un profilo sofisticato, con una complessità tutta sua.",
    "Fruttato":   "Una miscela gioiosa, con punte di dolcezza naturale.",
    "Umami":      "Un mix dal potere sinergico, che esalta ogni ingrediente.",
    "Salato":     "Una miscela sapida ed energica, che amplifica i sapori.",
}

USE_SUGGEST = {
    "Piccante":   "Ideale su carni grigliate, formaggi stagionati e piatti texani.",
    "Dolce":      "Perfetto come rub su costine, anatra glassata o dessert salati.",
    "Agrumato":   "Eccellente su pesce crudo, ceviche, carpacci e cocktail.",
    "Affumicato": "Straordinario su uova, burro, caramello salato e barbecue.",
    "Legnoso":    "Ideale in brasati, stufati lenti, selvaggina e formaggi duri.",
    "Floreale":   "Magnifico su salmone, capesante, dolci con panna e gin.",
    "Terroso":    "Ottimo in zuppe di legumi, curry, riso e piatti vegetariani.",
    "Erbaceo":    "Perfetto su verdure al forno, pasta fresca e formaggi freschi.",
    "Amaro":      "Interessante in salse complesse, cioccolato fondente e cocktail.",
    "Fruttato":   "Delizioso con carne di maiale, salmone e nei dessert fruttati.",
    "Umami":      "Potenzia brodi, risotti, steak e salse a lunga cottura.",
    "Salato":     "Perfetto a finire uova, avocado, caramello e carni bianche.",
}


def _compute_profile(selected_spices: list, quantities: dict) -> dict:
    """Calcola il profilo aromatico pesato sulla quantità."""
    totals = {}
    total_qty = sum(quantities.get(s, 1.0) for s in selected_spices)
    if total_qty == 0:
        return {}

    for sid in selected_spices:
        sp = SPICE_DICT.get(sid, {})
        frac = quantities.get(sid, 1.0) / total_qty
        for tag in sp.get("tags", []):
            weight = TAG_WEIGHTS.get(tag, 50)
            totals[tag] = totals.get(tag, 0) + frac * weight

    if not totals:
        return {}
    mx = max(totals.values())
    return {k: round(v / mx * 100) for k, v in totals.items()}


def _radar_svg(profile: dict) -> str:
    """Genera un radar chart SVG inline."""
    items = [(k, v) for k, v in profile.items() if v > 0]
    if not items:
        return "<div style='text-align:center;color:#666;padding:2rem;'>⚗️ Aggiungi spezie per vedere il profilo</div>"

    N = max(len(items), 3)
    cx, cy, r = 120, 120, 90
    step = 2 * math.pi / N

    # Grid rings
    rings_svg = ""
    for frac in [0.25, 0.5, 0.75, 1.0]:
        pts = " ".join(
            f"{cx + r*frac*math.cos(i*step - math.pi/2):.1f},{cy + r*frac*math.sin(i*step - math.pi/2):.1f}"
            for i in range(N)
        )
        rings_svg += f'<polygon points="{pts}" fill="none" stroke="rgba(201,144,12,0.12)" stroke-width="1"/>'

    # Axes
    axes_svg = ""
    for i in range(N):
        angle = i * step - math.pi / 2
        axes_svg += f'<line x1="{cx}" y1="{cy}" x2="{cx+r*math.cos(angle):.1f}" y2="{cy+r*math.sin(angle):.1f}" stroke="rgba(201,144,12,0.15)" stroke-width="1"/>'

    # Data
    data_pts = []
    labels_svg = ""
    dots_svg = ""
    for i, (tag, val) in enumerate(items):
        angle = i * step - math.pi / 2
        frac = val / 100
        px = cx + r * frac * math.cos(angle)
        py = cy + r * frac * math.sin(angle)
        data_pts.append(f"{px:.1f},{py:.1f}")
        dots_svg += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.5" fill="{GOLD}"/>'
        lx = cx + (r + 22) * math.cos(angle)
        ly = cy + (r + 22) * math.sin(angle)
        color = FLAVOR_TAG_COLORS.get(tag, "#888")
        labels_svg += f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" dominant-baseline="middle" font-size="9" fill="{color}" font-weight="600">{tag}</text>'

    polygon_pts = " ".join(data_pts)

    return f'''<svg viewBox="0 0 240 240" style="width:100%;max-width:280px;margin:0 auto;display:block;">
        {rings_svg}{axes_svg}
        <polygon points="{polygon_pts}" fill="rgba(201,144,12,0.2)" stroke="{GOLD}" stroke-width="1.5"/>
        {dots_svg}{labels_svg}
    </svg>'''


def _build_comment(profile: dict, spice_names: list) -> list:
    """Genera commento aromatico in 5 righe."""
    if not profile:
        return []
    ranked = sorted(profile.items(), key=lambda x: -x[1])
    top1, top2 = ranked[0][0], ranked[1][0] if len(ranked) > 1 else None
    top3 = ranked[2][0] if len(ranked) > 2 else None
    intensity = "molto pronunciata" if ranked[0][1] > 80 else "bilanciata" if ranked[0][1] > 50 else "delicata"

    line1 = OPENING.get(top1, "Un mix di grande personalità e complessità.")
    line2 = f"Il carattere {intensity} del {top1.lower()}" + (f" si fonde con note {top2.lower()}" + (f" e {top3.lower()}" if top3 else "") + ", creando una firma aromatica unica." if top2 else f" domina con eleganza la composizione.")
    names_str = ", ".join(spice_names[:-1]) + " e " + spice_names[-1] if len(spice_names) > 1 else spice_names[0]
    line3 = f"La sinergia tra {names_str} genera una complessità difficile da trovare nei mix commerciali."
    line4 = USE_SUGGEST.get(top1, "Si presta a molteplici abbinamenti sia in cucina calda che a crudo.")
    line5 = "Consiglio d'uso: aggiungilo a fine cottura per preservarne le note volatili" + (" — la potenza di questo mix richiede mano leggera." if ranked[0][1] > 75 else ".")

    return [line1, line2, line3, line4, line5]


def show():
    page_header("The Lab", "Crea le tue miscele personalizzate e visualizza il profilo aromatico", "⚗️")

    # ── State init ───────────────────────────────────────────
    if "lab_selected" not in st.session_state:
        st.session_state["lab_selected"] = []
    if "lab_quantities" not in st.session_state:
        st.session_state["lab_quantities"] = {}

    # ── Layout: selector + profile ───────────────────────────
    col_pick, col_profile = st.columns([1, 1])

    with col_pick:
        st.markdown(f"<div style='font-size:.75rem;color:#666;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.5rem;'>🧂 Seleziona spezie per il mix</div>", unsafe_allow_html=True)

        spice_names = sorted([s["name"] for s in SPICES_CATALOG])
        name_to_id = {s["name"]: s["id"] for s in SPICES_CATALOG}

        selected_names = st.multiselect(
            "Scegli spezie", spice_names,
            default=[SPICE_DICT[sid]["name"] for sid in st.session_state["lab_selected"] if sid in SPICE_DICT],
            key="lab_spice_picker",
            label_visibility="collapsed",
        )

        # Sync selection
        st.session_state["lab_selected"] = [name_to_id[n] for n in selected_names if n in name_to_id]

        # Quantità per ogni spezia selezionata
        if st.session_state["lab_selected"]:
            st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:.7rem;color:#666;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.5rem;'>⚖️ Composizione ({len(st.session_state['lab_selected'])} spezie)</div>", unsafe_allow_html=True)

            for sid in st.session_state["lab_selected"]:
                sp = SPICE_DICT[sid]
                tags_html = " ".join(
                    f'<span style="background:{FLAVOR_TAG_COLORS.get(t,GOLD)}18;color:{FLAVOR_TAG_COLORS.get(t,GOLD)};'
                    f'font-size:.6rem;padding:1px 6px;border-radius:99px;">{t}</span>'
                    for t in sp.get("tags", [])
                )
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.2rem;">
                      <span style="font-size:1.2rem;">{sp.get('emoji','🌿')}</span>
                      <span style="font-weight:600;color:#E8DCC8;font-size:.9rem;">{sp['name']}</span>
                    </div>
                    <div style="margin-bottom:.3rem;">{tags_html}</div>
                    """, unsafe_allow_html=True)
                with c2:
                    qty = st.number_input(
                        "Parti", min_value=0.25, max_value=10.0, value=st.session_state["lab_quantities"].get(sid, 1.0),
                        step=0.25, key=f"lab_qty_{sid}", label_visibility="collapsed",
                    )
                    st.session_state["lab_quantities"][sid] = qty

    # ── Profilo aromatico ────────────────────────────────────
    with col_profile:
        profile = _compute_profile(st.session_state["lab_selected"], st.session_state["lab_quantities"])

        st.markdown(f"<div style='font-size:.75rem;color:#666;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.5rem;text-align:center;'>📊 Profilo aromatico</div>", unsafe_allow_html=True)

        # Radar SVG
        st.markdown(_radar_svg(profile), unsafe_allow_html=True)

        # Barre aromatiche
        if profile:
            st.markdown("<div style='height:.75rem;'></div>", unsafe_allow_html=True)
            for tag, val in sorted(profile.items(), key=lambda x: -x[1]):
                color = FLAVOR_TAG_COLORS.get(tag, GOLD)
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.3rem;">
                  <div style="width:70px;font-size:.72rem;color:{color};font-weight:600;text-align:right;">{tag}</div>
                  <div style="flex:1;background:#222;border-radius:99px;height:8px;overflow:hidden;">
                    <div style="width:{val}%;height:100%;background:{color};border-radius:99px;"></div>
                  </div>
                  <div style="width:30px;font-size:.7rem;color:#888;text-align:right;">{val}%</div>
                </div>
                """, unsafe_allow_html=True)

        # Commento aromatico
        if profile and st.session_state["lab_selected"]:
            names = [SPICE_DICT[sid]["name"] for sid in st.session_state["lab_selected"]]
            lines = _build_comment(profile, names)
            if lines:
                st.markdown(f"""
                <div style="margin-top:1rem;padding:.85rem 1rem;background:rgba(201,144,12,0.05);
                            border:1px solid rgba(201,144,12,0.18);border-radius:10px;">
                  <div style="font-size:.62rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
                              color:{GOLD};margin-bottom:.4rem;">✦ Note del Mastro Speziiere</div>
                  <p style="font-size:.82rem;color:#E8DCC8;font-style:italic;font-weight:500;margin:0 0 .4rem;line-height:1.55;">{lines[0]}</p>
                  {''.join(f'<p style="font-size:.78rem;color:#aaa;margin:0 0 .3rem;line-height:1.55;">› {l}</p>' for l in lines[1:])}
                </div>
                """, unsafe_allow_html=True)

    # ── Salva miscela ────────────────────────────────────────
    if st.session_state["lab_selected"]:
        st.markdown("---")
        st.markdown(f"<div style='font-size:.75rem;color:#666;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.5rem;'>💾 Salva miscela</div>", unsafe_allow_html=True)

        with st.form("lab_save_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                mix_name = st.text_input("Nome del mix *", placeholder="es. BBQ Rub Estivo", key="lab_mix_name")
            with c2:
                mix_desc = st.text_area("Descrizione", placeholder="Note sulla miscela…", height=68, key="lab_mix_desc")

            if st.form_submit_button("💾 Salva Miscela", use_container_width=True):
                if not mix_name.strip():
                    st.error("Inserisci un nome per la miscela.")
                else:
                    uid = st.session_state["user_id"]
                    from utils.db import get_supabase
                    sb = get_supabase()
                    ingredients = [
                        {"spice_id": sid, "quantity": st.session_state["lab_quantities"].get(sid, 1.0)}
                        for sid in st.session_state["lab_selected"]
                    ]
                    top_tags = sorted(profile.items(), key=lambda x: -x[1])[:3]
                    sb.table("smp_mixes").insert({
                        "utente_id": uid,
                        "name": mix_name.strip(),
                        "description": mix_desc,
                        "ingredients": ingredients,
                        "tags": [t for t, _ in top_tags],
                    }).execute()
                    st.success(f"✅ Miscela «{mix_name}» salvata!")
                    st.session_state["lab_selected"] = []
                    st.session_state["lab_quantities"] = {}
                    st.rerun()
