import streamlit as st
from utils.db import get_supabase
from utils.ui import page_header, metric_card, GOLD, GREEN, AMBER, RED
from datetime import date

def show():
    uid  = st.session_state["user_id"]
    nome = st.session_state.get("user_nome", "Chef")
    sb   = get_supabase()

    # ── Welcome Hero ─────────────────────────────────────────
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#1A1200 0%,#0E0E0E 60%);
                border:1px solid {GOLD}33;border-radius:16px;padding:2rem 2.5rem;margin-bottom:1.5rem;">
      <div style="font-size:.7rem;color:#666;text-transform:uppercase;letter-spacing:.15em;">SpiceMaster Pro</div>
      <h1 style="font-size:2rem;color:{GOLD};margin:.25rem 0;font-weight:800;">
        👋 Benvenuto, {nome}
      </h1>
      <p style="color:#aaa;margin:0;font-size:.9rem;">Il tuo laboratorio botanico personale</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats rapide dalla dispensa ──────────────────────────
    rows = sb.table("smp_dispensa").select("*").eq("utente_id", uid).execute().data or []
    today = date.today().isoformat()
    total   = len(rows)
    low     = sum(1 for r in rows if (r.get("stock_level") or 100) < 25)
    expired = sum(1 for r in rows if r.get("expiration_date") and r["expiration_date"] < today)

    c1, c2, c3 = st.columns(3)
    with c1: metric_card("🧂 In Dispensa", str(total), "spezie registrate")
    with c2: metric_card("⚠️ Scorta Bassa", str(low), "sotto il 25%", color=RED if low else GREEN)
    with c3: metric_card("❌ Scadute",     str(expired), "da sostituire", color=RED if expired else GREEN)

    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

    # ── Navigazione rapida ───────────────────────────────────
    st.markdown(f"""
    <div style="font-size:.7rem;color:#666;text-transform:uppercase;letter-spacing:.12em;margin-bottom:.75rem;">
      Accesso rapido
    </div>
    """, unsafe_allow_html=True)

    nav1, nav2, nav3, nav4 = st.columns(4)

    NAV_CARDS = [
        ("🏺", "La Mia Dispensa",  f"{total} spezie personali",    GOLD,    "La tua collezione personale"),
        ("📚", "Catalogo Spezie",   "193 spezie e botaniche",       "#6B8E23","Esplora l'intero catalogo"),
        ("🍸", "The Gin Bar",       "49 gin con botaniche",         "#5A8AAF","Gin, botaniche e servizio"),
        ("📖", "Storico Utilizzi",  "Registro piatti e valutazioni","#9370DB","Traccia i tuoi esperimenti"),
    ]

    for col, (emoji, title, sub, color, desc) in zip([nav1,nav2,nav3,nav4], NAV_CARDS):
        with col:
            st.markdown(f"""
            <div style="background:#1A1A1A;border:1px solid {color}44;border-radius:14px;
                        padding:1.5rem 1.25rem;text-align:center;min-height:180px;
                        display:flex;flex-direction:column;justify-content:center;
                        transition:all .2s;">
              <div style="font-size:2.2rem;margin-bottom:.5rem;">{emoji}</div>
              <div style="font-weight:800;color:{color};font-size:1rem;margin-bottom:.3rem;">{title}</div>
              <div style="color:#888;font-size:.78rem;margin-bottom:.4rem;">{sub}</div>
              <div style="color:#555;font-size:.7rem;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align:center;color:#555;font-size:.75rem;margin-top:2rem;">
      ☝️ Usa le tab in alto per navigare tra le sezioni
    </div>
    """, unsafe_allow_html=True)

    # ── Spezie che richiedono attenzione ─────────────────────
    problemi = [r for r in rows if (r.get("stock_level") or 100) < 25 or (r.get("expiration_date") and r["expiration_date"] < today)]
    if problemi:
        st.markdown("---")
        st.markdown("### 🚨 Richiede attenzione")
        for r in problemi[:5]:
            lvl = r.get("stock_level", 100)
            exp = r.get("expiration_date", "")
            is_expired = exp and exp < today
            colore = RED if is_expired or lvl < 10 else AMBER
            st.markdown(f"""
            <div style="background:#1A1A1A;border:1px solid {colore}55;border-radius:10px;
                        padding:.8rem 1.1rem;margin-bottom:.4rem;display:flex;align-items:center;gap:1rem;">
              <div style="font-size:1.3rem;">{'❌' if is_expired else '⚠️'}</div>
              <div style="flex:1;">
                <b style="color:#E8DCC8;">{r['spice_name']}</b>
                <span style="color:#888;font-size:.78rem;margin-left:.5rem;">{r.get('brand','')}</span>
              </div>
              <div style="text-align:right;">
                <span style="color:{colore};font-weight:700;">{lvl}%</span>
                {'<br><span style="color:'+RED+';font-size:.72rem;">Scaduta: '+exp+'</span>' if is_expired else ''}
              </div>
            </div>
            """, unsafe_allow_html=True)
