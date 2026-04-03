import streamlit as st
from utils.db import get_supabase

def login_page():
    """Pagina di login — restituisce True se autenticato."""
    st.markdown("""
    <style>
    .login-box {
        max-width: 420px; margin: 4rem auto; padding: 2.5rem;
        background: #1A1A1A; border-radius: 16px;
        border: 1px solid #C9900C44;
        box-shadow: 0 8px 32px rgba(0,0,0,0.6), 0 0 0 1px #C9900C22;
    }
    .login-title { font-size: 2rem; font-weight: 800; color: #C9900C;
                   text-align: center; margin-bottom: 0.25rem; }
    .login-sub   { color: #888; text-align: center; margin-bottom: 2rem; font-style: italic; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-title">🌶️ SpiceMaster Pro</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-sub">Il tuo laboratorio botanico in cloud</div>', unsafe_allow_html=True)
        st.markdown("---")

        with st.form("login_form"):
            email    = st.text_input("📧 Email", placeholder="direzione@serrastudio.it")
            password = st.text_input("🔑 Password", type="password")
            submit   = st.form_submit_button("Accedi →", use_container_width=True)

        if submit:
            if not email or not password:
                st.error("Inserisci email e password.")
                return False
            sb = get_supabase()
            res = sb.table("smp_utenti")\
                    .select("id, nome, email")\
                    .eq("email", email)\
                    .eq("password_hash", password)\
                    .execute()
            if res.data:
                user = res.data[0]
                st.session_state["user_id"]   = user["id"]
                st.session_state["user_nome"] = user["nome"] or user["email"].split("@")[0]
                st.session_state["user_email"]= user["email"]
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("❌ Credenziali non corrette.")
        return False


def check_auth() -> bool:
    """Verifica se l'utente è loggato."""
    return st.session_state.get("logged_in", False)


def logout():
    for k in ["user_id", "user_nome", "user_email", "logged_in"]:
        st.session_state.pop(k, None)
    st.rerun()
