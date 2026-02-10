# auth_ui.py
import streamlit as st
from iam_workflow import get_token


def render_auth_status():
    token = get_token()
    source = st.session_state.get("auth_source", "github")

    # optional: user info if you store it later
    user = st.session_state.get("auth_user", {})
    login = user.get("login")
    name = user.get("name")

    if token:
        who = name or login or "GitHub user"
        prefix = token[:8]

        if source == "dev":
            st.markdown(
                f"""
                <div style="padding:10px;
                            border-radius:6px;
                            background:#fff3cd;
                            border:1px solid #ffeeba;
                            margin-bottom:0.75rem;">
                    🧪 <b>DEV AUTH ACTIVE</b><br>
                    Logged in as: <b>{who}</b><br>
                    Token: <code>{prefix}…</code>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div style="padding:10px;
                            border-radius:6px;
                            background:#d4edda;
                            border:1px solid #c3e6cb;
                            margin-bottom:0.75rem;">
                    ✅ <b>GitHub Login Successful</b><br>
                    Logged in as: <b>{who}</b>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            """
            <div style="padding:10px;
                        border-radius:6px;
                        background:#f8d7da;
                        border:1px solid #f5c6cb;
                        margin-bottom:0.75rem;">
                🔒 <b>Not authenticated</b>
            </div>
            """,
            unsafe_allow_html=True,
        )
