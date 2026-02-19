import streamlit as st
from iam_workflow import get_token, login_button, clear_auth

def render_auth_status():
    token = get_token()
    user = st.session_state.get("auth_user", {})

    if token:
        login = user.get("login")
        name = user.get("name")
        who = name or login or "GitHub user"

        st.success(f"✅ Logged in as {who}")

        if st.button("Logout"):
            clear_auth()
            st.rerun()

    else:
        st.warning("🔒 Not authenticated")
        login_button()
        st.stop()
