"""
SpiceMaster Pro — App Principale
Login + routing verso le sezioni
"""
import streamlit as st
from utils.auth import check_auth, login_page, logout
from utils.ui import page_header, metric_card, GOLD

st.set_page_config(
    page_title="SpiceMaster Pro",
    page_icon="🌶️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS Globale ────────────────────────────────────────────────
st.markdown("""
<style>
/* Nascondi header Streamlit default */
#MainMenu, footer, header { visibility: hidden; }
/* Sidebar */
[data-testid="stSidebar"] { background: #111 !important; border-right: 1px solid #C9900C33; }
[data-testid="stSidebar"] .stRadio label { color: #E8DCC8 !important; }
/* Bottoni */
.stButton > button {
    background: linear-gradient(135deg, #C9900C, #F4A900);
    color: #000; font-weight: 700; border: none; border-radius: 8px;
}
.stButton > button:hover { opacity:.85; transform:translateY(-1px); }
/* Cards */
.card {
    background:#1A1A1A; border:1px solid #C9900C33;
    border-radius:12px; padding:1.2rem;
    margin-bottom:.75rem;
}
/* Input */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
    background:#1A1A1A !important; border:1px solid #C9900C44 !important;
    color:#E8DCC8 !important; border-radius:8px !important;
}
div[data-testid="metric-container"] {
    background:#1A1A1A; border:1px solid #C9900C33; border-radius:12px;
    padding:1rem;
}
</style>
""", unsafe_allow_html=True)

# ── AUTH ──────────────────────────────────────────────────────
if not check_auth():
    login_page()
    st.stop()

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center;padding:1.2rem 0 .75rem;">
      <div style="font-size:2.2rem;">🌶️</div>
      <div style="font-size:1.1rem;font-weight:800;color:#C9900C;">SpiceMaster Pro</div>
      <div style="font-size:.72rem;color:#666;margin-top:.2rem;">Laboratorio Botanico</div>
    </div>
    <hr style="border-color:#C9900C33;margin:.5rem 0 1rem;">
    """, unsafe_allow_html=True)

    nome = st.session_state.get("user_nome", "Chef")
    st.markdown(f"<div style='color:#888;font-size:.78rem;text-align:center;margin-bottom:1rem;'>👋 Benvenuto, <b style='color:#C9900C;'>{nome}</b></div>", unsafe_allow_html=True)

    pagina = st.radio(
        "Navigazione",
        ["📊 Dashboard", "🏺 La Mia Dispensa", "📚 Catalogo Spezie", "🍸 The Gin Bar", "📖 Storico"],
        label_visibility="collapsed",
    )
    st.markdown("<hr style='border-color:#C9900C33;margin:1rem 0;'>", unsafe_allow_html=True)
    if st.button("🚪 Esci", use_container_width=True):
        logout()

# ── ROUTING ───────────────────────────────────────────────────
if pagina == "📊 Dashboard":
    from pages import dashboard; dashboard.show()
elif pagina == "🏺 La Mia Dispensa":
    from pages import dispensa; dispensa.show()
elif pagina == "📚 Catalogo Spezie":
    from pages import catalogo; catalogo.show()
elif pagina == "🍸 The Gin Bar":
    from pages import gin_bar; gin_bar.show()
elif pagina == "📖 Storico":
    from pages import history; history.show()
