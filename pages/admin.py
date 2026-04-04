import streamlit as st
from utils.db import get_supabase
from utils.ui import page_header, GOLD, GREEN, RED, AMBER
from utils.auth import is_admin

def show():
    if not is_admin():
        st.warning("⛔ Accesso riservato all'amministratore.")
        return

    page_header("Gestione Utenti", "Pannello di amministrazione", "👥")

    sb = get_supabase()
    users = sb.table("smp_utenti").select("*").order("id").execute().data or []

    # ── Statistiche ──────────────────────────────────────────
    total = len(users)
    active = sum(1 for u in users if u.get("ruolo") != "disabilitato")
    admins = sum(1 for u in users if u.get("ruolo") == "admin")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div style="background:#1A1A1A;border:1px solid {GOLD}33;border-radius:12px;padding:1rem;text-align:center;"><div style="font-size:.65rem;color:#888;text-transform:uppercase;letter-spacing:.1em;">Utenti totali</div><div style="font-size:2rem;font-weight:800;color:{GOLD};">{total}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div style="background:#1A1A1A;border:1px solid {GREEN}33;border-radius:12px;padding:1rem;text-align:center;"><div style="font-size:.65rem;color:#888;text-transform:uppercase;letter-spacing:.1em;">Attivi</div><div style="font-size:2rem;font-weight:800;color:{GREEN};">{active}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div style="background:#1A1A1A;border:1px solid #9370DB33;border-radius:12px;padding:1rem;text-align:center;"><div style="font-size:.65rem;color:#888;text-transform:uppercase;letter-spacing:.1em;">Admin</div><div style="font-size:2rem;font-weight:800;color:#9370DB;">{admins}</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    # ── Lista utenti ─────────────────────────────────────────
    ROLE_COLORS = {"admin": "#9370DB", "utente": GREEN, "disabilitato": RED}
    ROLE_ICONS  = {"admin": "👑", "utente": "👤", "disabilitato": "🚫"}

    for u in users:
        ruolo = u.get("ruolo", "utente")
        rc = ROLE_COLORS.get(ruolo, "#888")
        ri = ROLE_ICONS.get(ruolo, "👤")
        email = u.get("email", "—")
        nome = u.get("nome", "—")

        # Conta spezie in dispensa
        disp_count = len(sb.table("smp_dispensa").select("id").eq("utente_id", u["id"]).execute().data or [])

        card = f'<div style="background:#1A1A1A;border:1px solid {rc}44;border-radius:12px;padding:1rem 1.25rem;margin-bottom:.5rem;display:flex;align-items:center;gap:1rem;">'
        card += f'<div style="width:40px;height:40px;background:{rc}22;border:1px solid {rc}55;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.3rem;">{ri}</div>'
        card += f'<div style="flex:1;">'
        card += f'<div style="font-weight:700;color:#E8DCC8;">{nome}</div>'
        card += f'<div style="font-size:.78rem;color:#888;">{email}</div>'
        card += f'</div>'
        card += f'<div style="text-align:right;">'
        card += f'<span style="background:{rc}22;color:{rc};border:1px solid {rc}55;border-radius:99px;padding:2px 10px;font-size:.7rem;font-weight:600;">{ruolo}</span>'
        card += f'<div style="font-size:.7rem;color:#666;margin-top:.3rem;">🧂 {disp_count} spezie</div>'
        card += f'</div></div>'
        st.markdown(card, unsafe_allow_html=True)

        # Azioni per ogni utente (non per sé stessi)
        if email != st.session_state.get("user_email"):
            ac1, ac2, ac3 = st.columns(3)
            with ac1:
                new_role = "disabilitato" if ruolo != "disabilitato" else "utente"
                btn_label = "🚫 Disabilita" if ruolo != "disabilitato" else "✅ Riabilita"
                if st.button(btn_label, key=f"toggle_{u['id']}", use_container_width=True):
                    sb.table("smp_utenti").update({"ruolo": new_role}).eq("id", u["id"]).execute()
                    st.rerun()
            with ac2:
                if ruolo != "admin":
                    if st.button("👑 Rendi Admin", key=f"admin_{u['id']}", use_container_width=True):
                        sb.table("smp_utenti").update({"ruolo": "admin"}).eq("id", u["id"]).execute()
                        st.rerun()
                else:
                    if st.button("👤 Rendi Utente", key=f"demote_{u['id']}", use_container_width=True):
                        sb.table("smp_utenti").update({"ruolo": "utente"}).eq("id", u["id"]).execute()
                        st.rerun()
            with ac3:
                if st.button("🔑 Reset Pass", key=f"resetpw_{u['id']}", use_container_width=True):
                    sb.table("smp_utenti").update({"password_hash": "CambiaMe2024!"}).eq("id", u["id"]).execute()
                    st.success(f"Password di {nome} reimpostata a 'CambiaMe2024!'")

    # ── Aggiungi utente manualmente ──────────────────────────
    st.markdown("---")
    with st.expander("➕ Aggiungi utente manualmente"):
        with st.form("admin_add_user"):
            c1, c2 = st.columns(2)
            with c1:
                new_name  = st.text_input("Nome", key="adm_name")
                new_email = st.text_input("Email", key="adm_email")
            with c2:
                new_pass  = st.text_input("Password", value="CambiaMe2024!", key="adm_pass")
                new_role  = st.selectbox("Ruolo", ["utente", "admin"], key="adm_role")
            if st.form_submit_button("✓ Crea utente", use_container_width=True):
                if not new_email:
                    st.error("Email obbligatoria.")
                else:
                    existing = sb.table("smp_utenti").select("id").eq("email", new_email.strip().lower()).execute()
                    if existing.data:
                        st.error("Email già registrata.")
                    else:
                        sb.table("smp_utenti").insert({
                            "nome": new_name.strip(),
                            "email": new_email.strip().lower(),
                            "password_hash": new_pass,
                            "ruolo": new_role,
                        }).execute()
                        st.success(f"✅ Utente {new_name} creato!")
                        st.rerun()
