import streamlit as st
import bcrypt
from html import escape
from utils.db import get_supabase
from utils.ui import GOLD
from datetime import datetime

ADMIN_EMAIL = "direzione@serrastudio.it"


# ── Password hashing ────────────────────────────────────────
def _hash_pw(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_pw(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        # Fallback: confronto diretto per password non ancora migrate
        return password == hashed


# ── Notifica admin ───────────────────────────────────────────
def _notify_admin_registration(nome: str, email: str):
    """Notifica l'admin di una nuova registrazione via email."""
    try:
        import smtplib
        from email.mime.text import MIMEText
        smtp_host = st.secrets.get("SMTP_HOST", "")
        smtp_port = int(st.secrets.get("SMTP_PORT", 587))
        smtp_user = st.secrets.get("SMTP_USER", "")
        smtp_pass = st.secrets.get("SMTP_PASS", "")
        if smtp_host and smtp_user:
            msg = MIMEText(
                f"Nuovo utente registrato su SpiceMaster Pro:\n\n"
                f"Nome: {nome}\nEmail: {email}\n"
                f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                f"Accedi al pannello Admin per gestirlo."
            )
            msg["Subject"] = f"🌶️ SpiceMaster Pro — Nuovo utente: {nome}"
            msg["From"] = smtp_user
            msg["To"] = ADMIN_EMAIL
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_user, ADMIN_EMAIL, msg.as_string())
    except Exception:
        pass


# ── Pagina di login ──────────────────────────────────────────
def login_page():
    """Pagina di login con registrazione."""
    st.markdown("""
    <style>
    .auth-box {
        max-width: 440px; margin: 2rem auto; padding: 2.5rem;
        background: #1A1A1A; border-radius: 16px;
        border: 1px solid #C9900C44;
        box-shadow: 0 8px 32px rgba(0,0,0,0.6), 0 0 0 1px #C9900C22;
    }
    .auth-title { font-size: 2rem; font-weight: 800; color: #C9900C;
                   text-align: center; margin-bottom: 0.25rem; }
    .auth-sub   { color: #888; text-align: center; margin-bottom: 1.5rem;
                   font-style: italic; font-size: .9rem; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="auth-title">🌶️ SpiceMaster Pro</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-sub">Il tuo laboratorio botanico in cloud</div>', unsafe_allow_html=True)

        if "auth_mode" not in st.session_state:
            st.session_state["auth_mode"] = "login"

        mode = st.session_state["auth_mode"]

        # ── LOGIN ────────────────────────────────────────────
        if mode == "login":
            with st.form("login_form"):
                email    = st.text_input("📧 Email", placeholder="la-tua@email.it", key="login_email")
                password = st.text_input("🔑 Password", type="password", key="login_pass")
                submit   = st.form_submit_button("Accedi →", use_container_width=True)

            if submit:
                if not email or not password:
                    st.error("Inserisci email e password.")
                else:
                    sb = get_supabase()
                    res = sb.table("smp_utenti")\
                            .select("id, nome, email, ruolo, password_hash")\
                            .eq("email", email.strip().lower())\
                            .execute()
                    if res.data:
                        user = res.data[0]
                        if not _verify_pw(password, user["password_hash"]):
                            st.error("❌ Credenziali non corrette.")
                        elif user.get("ruolo") == "disabilitato":
                            st.error("⛔ Account disabilitato. Contatta l'amministratore.")
                        else:
                            # Migra password in chiaro a bcrypt se necessario
                            if not user["password_hash"].startswith("$2"):
                                sb.table("smp_utenti").update({
                                    "password_hash": _hash_pw(password)
                                }).eq("id", user["id"]).execute()
                            st.session_state["user_id"]    = user["id"]
                            st.session_state["user_nome"]  = user["nome"] or user["email"].split("@")[0]
                            st.session_state["user_email"] = user["email"]
                            st.session_state["user_ruolo"] = user.get("ruolo", "utente")
                            st.session_state["logged_in"]  = True
                            st.rerun()
                    else:
                        st.error("❌ Credenziali non corrette.")

            c1, c2 = st.columns(2)
            with c1:
                if st.button("📝 Registrati", key="goto_register", use_container_width=True):
                    st.session_state["auth_mode"] = "register"
                    st.rerun()
            with c2:
                if st.button("🔑 Password dimenticata", key="goto_reset", use_container_width=True):
                    st.session_state["auth_mode"] = "reset"
                    st.rerun()

        # ── REGISTRAZIONE ────────────────────────────────────
        elif mode == "register":
            st.markdown(f"<h3 style='color:{GOLD};text-align:center;'>📝 Registrazione</h3>", unsafe_allow_html=True)

            with st.form("register_form"):
                reg_nome  = st.text_input("👤 Nome", placeholder="Mario Rossi", key="reg_nome")
                reg_email = st.text_input("📧 Email", placeholder="mario@email.it", key="reg_email")
                reg_pass  = st.text_input("🔑 Password", type="password", key="reg_pass")
                reg_pass2 = st.text_input("🔑 Conferma Password", type="password", key="reg_pass2")
                submit    = st.form_submit_button("✓ Crea account", use_container_width=True)

            if submit:
                if not reg_email or not reg_pass:
                    st.error("Email e password sono obbligatori.")
                elif reg_pass != reg_pass2:
                    st.error("Le password non corrispondono.")
                elif len(reg_pass) < 6:
                    st.error("La password deve avere almeno 6 caratteri.")
                else:
                    sb = get_supabase()
                    existing = sb.table("smp_utenti").select("id").eq("email", reg_email.strip().lower()).execute()
                    if existing.data:
                        st.error("❌ Email già registrata. Prova ad accedere.")
                    else:
                        sb.table("smp_utenti").insert({
                            "nome": escape(reg_nome.strip()),
                            "email": reg_email.strip().lower(),
                            "password_hash": _hash_pw(reg_pass),
                            "ruolo": "utente",
                        }).execute()
                        _notify_admin_registration(reg_nome.strip(), reg_email.strip().lower())
                        st.success("✅ Account creato! Ora puoi accedere.")
                        st.session_state["auth_mode"] = "login"
                        st.rerun()

            if st.button("← Torna al login", key="back_from_register", use_container_width=True):
                st.session_state["auth_mode"] = "login"
                st.rerun()

        # ── RESET PASSWORD ───────────────────────────────────
        elif mode == "reset":
            st.markdown(f"<h3 style='color:{GOLD};text-align:center;'>🔑 Password dimenticata</h3>", unsafe_allow_html=True)
            st.info("📧 Per reimpostare la password, contatta l'amministratore all'indirizzo **direzione@serrastudio.it** indicando il tuo nome e l'email di registrazione.")
            st.markdown("<div style='height:.5rem;'></div>", unsafe_allow_html=True)

            if st.button("← Torna al login", key="back_from_reset", use_container_width=True):
                st.session_state["auth_mode"] = "login"
                st.rerun()

    return False


# ── Utility ──────────────────────────────────────────────────
def check_auth() -> bool:
    return st.session_state.get("logged_in", False)


def is_admin() -> bool:
    return st.session_state.get("user_ruolo", "") == "admin"


def logout():
    for k in ["user_id", "user_nome", "user_email", "user_ruolo", "logged_in", "auth_mode"]:
        st.session_state.pop(k, None)
    st.rerun()
