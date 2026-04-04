import streamlit as st
from utils.db import get_supabase
from utils.ui import page_header, stock_bar, spice_badge, GOLD, RED, AMBER, GREEN
from data.catalog import SPICE_DICT, SPICES_CATALOG, ALL_CATEGORIES
from datetime import date, timedelta

def _expiry_status(exp_str: str) -> tuple[str, str]:
    if not exp_str: return "ok", "—"
    d = date.fromisoformat(exp_str)
    today = date.today()
    if d < today:              return "danger", "❌ Scaduta"
    if d < today + timedelta(days=60): return "warn",   "⚠️ Presto"
    return "ok", "✓ Ok"

def show():
    page_header("La Mia Dispensa", "Il tuo inventario personale di spezie botaniche", "🏺")
    uid = st.session_state["user_id"]
    sb  = get_supabase()

    rows = sb.table("smp_dispensa").select("*").eq("utente_id", uid)\
             .order("spice_name").execute().data or []

    # ── Filtri ───────────────────────────────────────────────
    fc, fs, ft = st.columns([2,2,1])
    with fc:
        search = st.text_input("🔍 Cerca", placeholder="Pepe, Lavanda…", label_visibility="collapsed", key="disp_search")
    with fs:
        cat_filter = st.selectbox("Categoria", ["Tutte"] + ALL_CATEGORIES, label_visibility="collapsed", key="disp_category")
    with ft:
        only_low = st.checkbox("Solo scorta bassa", key="disp_lowstock")

    # Filtra
    filtered = rows
    if search:
        s = search.lower()
        filtered = [r for r in filtered if s in r["spice_name"].lower() or s in (r.get("brand","") or "").lower()]
    if cat_filter != "Tutte":
        filtered = [r for r in filtered if SPICE_DICT.get(r["spice_id"],{}).get("category") == cat_filter]
    if only_low:
        filtered = [r for r in filtered if (r.get("stock_level") or 100) < 25]

    st.markdown(f"<div style='color:#888;font-size:.8rem;margin-bottom:.75rem;'>{len(filtered)} spezie trovate</div>", unsafe_allow_html=True)

    # ── Grid card ────────────────────────────────────────────
    if not filtered:
        st.info("Nessuna spezia trovata. Aggiungine una!")
    else:
        cols = st.columns(3)
        for i, r in enumerate(filtered):
            sp       = SPICE_DICT.get(r["spice_id"], {})
            lvl      = r.get("stock_level", 100)
            brand    = r.get("brand", "")
            exp      = r.get("expiration_date", "")
            est, elbl= _expiry_status(exp)
            color    = sp.get("color","#C9900C")
            emoji    = sp.get("emoji","🌿")
            cat_lbl  = spice_badge(sp.get("category","?"))
            ec       = {"ok":GREEN,"warn":AMBER,"danger":RED}[est]

            with cols[i % 3]:
                with st.container():
                    bar_html = stock_bar(lvl)
                    st.markdown(f"""
                    <div style="background:#1A1A1A;border:1px solid {color}44;border-radius:12px;
                                padding:1.1rem;margin-bottom:.75rem;">
                      <div style="display:flex;align-items:center;gap:.75rem;margin-bottom:.6rem;">
                        <div style="width:44px;height:44px;background:{color}22;border:1px solid {color}55;
                                    border-radius:10px;display:flex;align-items:center;
                                    justify-content:center;font-size:1.3rem;flex-shrink:0;">{emoji}</div>
                        <div style="flex:1;min-width:0;">
                          <div style="font-weight:700;color:#E8DCC8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{r['spice_name']}</div>
                          <div style="font-size:.72rem;color:#888;">{brand}</div>
                        </div>
                      </div>
                      <div style="display:flex;gap:.4rem;flex-wrap:wrap;margin-bottom:.6rem;">
                        {cat_lbl}
                        <span style="background:{ec}22;color:{ec};border:1px solid {ec}55;
                                     border-radius:99px;padding:2px 8px;font-size:.7rem;">{elbl}</span>
                      </div>
                      {bar_html}
                      <div style="font-size:.7rem;color:#666;margin-top:.4rem;">
                        Scade: {exp or '—'}
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✏️ Modifica", key=f"edit_{r['id']}", use_container_width=True):
                            st.session_state["edit_item"] = r
                    with c2:
                        if st.button("🗑️ Rimuovi", key=f"del_{r['id']}", use_container_width=True):
                            sb.table("smp_dispensa").delete().eq("id", r["id"]).execute()
                            st.rerun()

    st.markdown("---")

    # ── Form aggiunta ────────────────────────────────────────
    with st.expander("➕ Aggiungi spezia alla dispensa", expanded=False):
        spice_options = {s["name"]: s["id"] for s in sorted(SPICES_CATALOG, key=lambda x: x["name"])}
        with st.form("add_spice_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                sel_name = st.selectbox("Spezia *", list(spice_options.keys()), key="disp_add_spice")
                brand    = st.text_input("Brand / Provenienza", placeholder="es. Terre Esotiche", key="disp_add_brand")
                stock    = st.slider("Scorta %", 0, 100, 100, key="disp_add_stock")
            with col2:
                purchase = st.date_input("Data acquisto", value=date.today(), key="disp_add_purchase")
                expiry   = st.date_input("Scadenza", value=date.today().replace(year=date.today().year+1), key="disp_add_expiry")
                notes    = st.text_area("Note", placeholder="Appunti…", height=80, key="disp_add_notes")
            submit = st.form_submit_button("✓ Aggiungi", use_container_width=True)
            if submit:
                spice_id = spice_options[sel_name]
                sb.table("smp_dispensa").insert({
                    "utente_id": uid, "spice_id": spice_id,
                    "spice_name": sel_name, "brand": brand,
                    "stock_level": stock,
                    "purchase_date": str(purchase), "expiration_date": str(expiry),
                    "notes": notes,
                }).execute()
                st.success(f"✅ {sel_name} aggiunta alla dispensa!")
                st.rerun()

    # ── Modal modifica ───────────────────────────────────────
    if "edit_item" in st.session_state and st.session_state["edit_item"]:
        r = st.session_state["edit_item"]
        with st.expander(f"✏️ Modifica: {r['spice_name']}", expanded=True):
            with st.form(f"edit_form_{r['id']}"):
                col1, col2 = st.columns(2)
                with col1:
                    new_brand = st.text_input("Brand", value=r.get("brand",""))
                    new_stock = st.slider("Scorta %", 0, 100, r.get("stock_level",100))
                with col2:
                    new_exp   = st.date_input("Scadenza", value=date.fromisoformat(r["expiration_date"]) if r.get("expiration_date") else date.today())
                    new_notes = st.text_area("Note", value=r.get("notes",""), height=80)
                c1, c2 = st.columns(2)
                with c1:
                    if st.form_submit_button("💾 Salva", use_container_width=True):
                        sb.table("smp_dispensa").update({
                            "brand": new_brand, "stock_level": new_stock,
                            "expiration_date": str(new_exp), "notes": new_notes,
                        }).eq("id", r["id"]).execute()
                        del st.session_state["edit_item"]
                        st.rerun()
                with c2:
                    if st.form_submit_button("✕ Annulla", use_container_width=True):
                        del st.session_state["edit_item"]
                        st.rerun()
