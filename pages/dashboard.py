import streamlit as st
from utils.db import get_supabase
from utils.ui import page_header, metric_card, stock_bar, GREEN, AMBER, RED
from datetime import date

def show():
    page_header("Dashboard", "Il tuo arsenale botanico a colpo d'occhio", "📊")
    uid = st.session_state["user_id"]
    sb  = get_supabase()

    # ── Carica dati ──────────────────────────────────────────
    rows = sb.table("smp_dispensa").select("*").eq("utente_id", uid).execute().data or []
    today = date.today().isoformat()
    total       = len(rows)
    scadute     = sum(1 for r in rows if r.get("expiration_date") and r["expiration_date"] < today)
    esaurimento = sum(1 for r in rows if (r.get("stock_level") or 100) < 25)
    presto      = sum(1 for r in rows if r.get("expiration_date") and today <= r["expiration_date"] <= str(date.today().replace(month=date.today().month+2 if date.today().month<=10 else 1)))

    # ── Metriche ─────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("🧂 Spezie in Dispensa", str(total), "totale registrate")
    with c2: metric_card("⚠️ Scorta Bassa",   str(esaurimento), "sotto il 25%",   color=RED if esaurimento else "#5A9A3A")
    with c3: metric_card("📅 In Scadenza",     str(presto),      "entro 60 giorni",color=AMBER if presto else "#5A9A3A")
    with c4: metric_card("❌ Scadute",         str(scadute),     "da rimuovere",   color=RED if scadute else "#5A9A3A")

    st.markdown("---")

    # ── Spezie con scorta bassa ───────────────────────────────
    if esaurimento or scadute:
        st.markdown("### 🚨 Richiede attenzione")
        problemi = [r for r in rows if (r.get("stock_level") or 100) < 25 or (r.get("expiration_date") and r["expiration_date"] < today)]
        for r in problemi:
            lvl  = r.get("stock_level", 100)
            exp  = r.get("expiration_date", "")
            expired = exp and exp < today
            colore  = RED if expired or lvl < 10 else AMBER
            st.markdown(f"""
            <div style="background:#1A1A1A;border:1px solid {colore}55;border-radius:10px;
                        padding:.9rem 1.2rem;margin-bottom:.5rem;display:flex;align-items:center;gap:1rem;">
              <div style="font-size:1.5rem;">{'❌' if expired else '⚠️'}</div>
              <div style="flex:1;">
                <b style="color:#E8DCC8;">{r['spice_name']}</b>
                <span style="color:#888;font-size:.8rem;margin-left:.5rem;">{r.get('brand','')}</span>
              </div>
              <div style="text-align:right;">
                <span style="color:{colore};font-weight:700;">{lvl}%</span>
                {'<br><span style="color:'+RED+';font-size:.75rem;">Scaduta: '+exp+'</span>' if expired else ''}
              </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("")

    # ── Distribuzione per categoria ───────────────────────────
    st.markdown("### 📊 Distribuzione Dispensa")
    if rows:
        from data.catalog import SPICE_DICT
        cats = {}
        for r in rows:
            sp = SPICE_DICT.get(r["spice_id"], {})
            cat = sp.get("category", "Altro")
            cats[cat] = cats.get(cat, 0) + 1
        import plotly.express as px
        import pandas as pd
        df = pd.DataFrame(list(cats.items()), columns=["Categoria","Quantità"])
        fig = px.pie(df, names="Categoria", values="Quantità",
                     color_discrete_sequence=["#C9900C","#5A9A3A","#6B4A9A","#5A8AAF","#C46060"],
                     hole=0.45)
        fig.update_layout(paper_bgcolor="#0E0E0E", plot_bgcolor="#0E0E0E",
                          font_color="#E8DCC8", legend_bgcolor="#1A1A1A",
                          margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aggiungi spezie alla tua dispensa per vedere le statistiche.")
