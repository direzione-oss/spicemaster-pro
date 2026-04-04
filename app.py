"""
SpiceMaster Pro — App Principale
Login + navigazione a pagina singola (no tabs, no sidebar)
"""
import streamlit as st
from utils.auth import check_auth, login_page, logout, is_admin
from utils.ui import GOLD

st.set_page_config(
    page_title="SpiceMaster Pro",
    page_icon="🌶️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS Globale ────────────────────────────────────────────────
st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"],
[data-testid="collapsedControl"] { display: none !important; }
.stButton > button {
    background: linear-gradient(135deg, #C9900C, #F4A900);
    color: #000; font-weight: 700; border: none; border-radius: 8px;
}
.stButton > button:hover { opacity:.85; transform:translateY(-1px); }
.stTextInput input, .stTextArea textarea, .stSelectbox select {
    background:#1A1A1A !important; border:1px solid #C9900C44 !important;
    color:#E8DCC8 !important; border-radius:8px !important;
}
</style>
""", unsafe_allow_html=True)

# ── AUTH ──────────────────────────────────────────────────────
if not check_auth():
    login_page()
    st.stop()

# ── HEADER + NAV ─────────────────────────────────────────────
nome = st.session_state.get("user_nome", "Chef")

# Pagine disponibili in base al ruolo
if is_admin():
    pages = ["👥 Admin", "🏠 Home", "🏺 Dispensa", "📚 Catalogo", "⚗️ Lab", "🍸 Gin Bar", "📖 Storico"]
else:
    pages = ["🏠 Home", "🏺 Dispensa", "📚 Catalogo", "⚗️ Lab", "🍸 Gin Bar", "📖 Storico"]

col_logo, col_nav, col_user = st.columns([2, 6, 1])
with col_logo:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:.6rem;padding:.3rem 0;">
      <span style="font-size:1.6rem;">🌶️</span>
      <span style="font-size:1.1rem;font-weight:800;color:{GOLD};">SpiceMaster Pro</span>
    </div>
    """, unsafe_allow_html=True)

with col_nav:
    pagina = st.radio(
        "nav", pages,
        horizontal=True, label_visibility="collapsed", key="main_nav"
    )

with col_user:
    if st.button("🚪 Esci", key="logout_btn"):
        logout()

st.markdown("<hr style='border-color:#C9900C22;margin:.5rem 0 1rem;'>", unsafe_allow_html=True)

# ── ROUTING ──────────────────────────────────────────────────
if pagina == "👥 Admin":
    from pages import admin; admin.show()
elif pagina == "🏠 Home":
    from pages import home; home.show()
elif pagina == "🏺 Dispensa":
    from pages import dispensa; dispensa.show()
elif pagina == "📚 Catalogo":
    from pages import catalogo; catalogo.show()
elif pagina == "⚗️ Lab":
    from pages import lab; lab.show()
elif pagina == "🍸 Gin Bar":
    from pages import gin_bar; gin_bar.show()
elif pagina == "📖 Storico":
    from pages import history; history.show()
