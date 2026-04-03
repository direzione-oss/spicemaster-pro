import streamlit as st
from utils.db import get_supabase
from utils.ui import page_header, GOLD, AMBER
from datetime import date

def show():
    page_header("Storico Utilizzi", "Registro dei piatti preparati e valutazioni", "📖")
    uid = st.session_state["user_id"]
    sb  = get_supabase()

    rows = sb.table("smp_history").select("*").eq("utente_id", uid)\
             .order("date", desc=True).execute().data or []

    STARS = ["","⭐","⭐⭐","⭐⭐⭐","⭐⭐⭐⭐","⭐⭐⭐⭐⭐"]

    if not rows:
        st.info("Nessuna voce nello storico. Aggiungi il tuo primo piatto!")
    else:
        for r in rows:
            rating = r.get("rating",3)
            st.markdown(f"""
            <div style="background:#1A1A1A;border:1px solid {GOLD}33;border-radius:12px;
                        padding:1rem 1.25rem;margin-bottom:.6rem;">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                  <b style="color:#E8DCC8;font-size:1rem;">{r.get('dish_name','—')}</b>
                  <span style="color:#666;font-size:.75rem;margin-left:.75rem;">{r.get('date','')}</span>
                </div>
                <span style="font-size:1.1rem;">{STARS[min(rating,5)]}</span>
              </div>
              {"<div style='color:#aaa;font-size:.82rem;margin-top:.4rem;'>"+r['notes']+"</div>" if r.get('notes') else ""}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    with st.expander("➕ Aggiungi utilizzo", expanded=False):
        from data.catalog import SPICES_CATALOG
        spice_opts = {s["name"]: s["id"] for s in sorted(SPICES_CATALOG, key=lambda x: x["name"])}
        with st.form("history_form", clear_on_submit=True):
            dish   = st.text_input("Nome piatto *", placeholder="es. Risotto allo Zafferano")
            sel    = st.multiselect("Spezie usate", list(spice_opts.keys()))
            rating = st.slider("Valutazione ⭐", 1, 5, 4)
            notes  = st.text_area("Note", placeholder="Impressioni, variazioni…", height=80)
            d      = st.date_input("Data", value=date.today())
            if st.form_submit_button("✓ Registra", use_container_width=True):
                if not dish:
                    st.error("Inserisci il nome del piatto.")
                else:
                    sb.table("smp_history").insert({
                        "utente_id": uid, "dish_name": dish,
                        "spice_ids": [spice_opts[s] for s in sel],
                        "rating": rating, "notes": notes, "date": str(d),
                    }).execute()
                    st.success("✅ Utilizzo registrato!")
                    st.rerun()
