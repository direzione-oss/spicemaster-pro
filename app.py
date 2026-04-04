"""
SpiceMaster Pro — App Principale
Login + navigazione a tab (no sidebar)
"""
import streamlit as st
from utils.auth import check_auth, login_page, logout
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
/* Nascondi sidebar, header e footer default */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"],
[data-testid="collapsedControl"] { display: none !important; }
/* Bottoni */
.stButton > button {
    background: linear-gradient(135deg, #C9900C, #F4A900);
    color: #000; font-weight: 700; border: none; border-radius: 8px;
}
.stButton > button:hover { opacity:.85; transform:translateY(-1px); }
/* Input */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
    background:#1A1A1A !important; border:1px solid #C9900C44 !important;
    color:#E8DCC8 !important; border-radius:8px !important;
}
/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: #111;
    border-radius: 12px;
    padding: 4px;
    border: 1px solid #C9900C33;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: #888;
    font-weight: 600;
    padding: 8px 16px;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #C9900C, #F4A900) !important;
    color: #000 !important;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ── AUTH ──────────────────────────────────────────────────────
if not check_auth():
    login_page()
    st.stop()

# ── HEADER ───────────────────────────────────────────────────
nome = st.session_state.get("user_nome", "Chef")
col_logo, col_user = st.columns([6, 1])
with col_logo:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:.75rem;padding:.5rem 0;">
      <span style="font-size:1.8rem;">🌶️</span>
      <div>
        <span style="font-size:1.2rem;font-weight:800;color:{GOLD};">SpiceMaster Pro</span>
        <span style="font-size:.72rem;color:#666;margin-left:.5rem;">Laboratorio Botanico</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
with col_user:
    st.markdown(f"<div style='text-align:right;padding-top:.6rem;'><span style='color:#888;font-size:.78rem;'>👋 <b style=\"color:{GOLD};\">{nome}</b></span></div>", unsafe_allow_html=True)
    if st.button("🚪 Esci", key="logout_btn"):
        logout()

# ── NAVIGAZIONE A TAB ────────────────────────────────────────
tab_dash, tab_disp, tab_cat, tab_gin, tab_hist = st.tabs([
    "📊 Dashboard",
    "🏺 Dispensa",
    "📚 Catalogo",
    "🍸 Gin Bar",
    "📖 Storico",
])

with tab_dash:
    from pages import dashboard; dashboard.show()

with tab_disp:
    from pages import dispensa; dispensa.show()

with tab_cat:
    from pages import catalogo; catalogo.show()

with tab_gin:
    from pages import gin_bar; gin_bar.show()

with tab_hist:
    from pages import history; history.show()
