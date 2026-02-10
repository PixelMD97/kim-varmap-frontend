import os
from datetime import datetime

import streamlit as st
import requests


# -------------------------------------------------
# Constants / keys
# -------------------------------------------------
AUTH_LOG_KEY = "auth_log"
AUTH_SOURCE_KEY = "auth_source"   # "dev" | "github"
TOKEN_KEY = "access_token"

BACKEND_URL = os.getenv(
    "KIM_API_BASE_URL",
    "https://2025varmapbackend-adgyb5eqghc6bzay.westeurope-01.azurewebsites.net/"
).rstrip("/")

FRONTEND_URL = os.getenv(
    "KIM_FRONTEND_URL",
    ""
).rstrip("/")


# -------------------------------------------------
# Internal auth logger (session-based, Streamlit-safe)
# -------------------------------------------------
def _log_auth(event: str, extra: dict | None = None):
    log = st.session_state.setdefault(AUTH_LOG_KEY, [])
    log.append({
        "ts": datetime.utcnow().isoformat(timespec="seconds"),
        "event": event,
        "extra": extra or {},
    })


# -------------------------------------------------
# Auth state helpers
# -------------------------------------------------
def get_token() -> str | None:
    return st.session_state.get(TOKEN_KEY)


def is_authenticated() -> bool:
    return bool(get_token())


def clear_auth():
    st.session_state.pop(TOKEN_KEY, None)
    st.session_state.pop(AUTH_SOURCE_KEY, None)


# -------------------------------------------------
# OAuth callback handling
# -------------------------------------------------
def handle_callback() -> bool:
    """
    Handle OAuth redirect back from backend.

    Expected query param:
      ?access_token=...

    Stores token + user info in session_state
    and restarts app in authenticated state.
    """
    if "access_token" not in st.query_params:
        return False

    token = st.query_params["access_token"]

    st.session_state[TOKEN_KEY] = token
    st.session_state[AUTH_SOURCE_KEY] = "github"

    # fetch user info ONCE
    try:
        resp = requests.get(
            f"{BACKEND_URL}/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        if resp.status_code == 200:
            st.session_state["auth_user"] = resp.json()
        else:
            st.session_state["auth_user"] = {}
    except Exception:
        st.session_state["auth_user"] = {}

    # clean URL + restart app
    st.query_params.clear()
    st.rerun()



# -------------------------------------------------
# Login button (redirect-based, no popup)
# -------------------------------------------------
def login_button():
    if not FRONTEND_URL:
        st.error("FRONTEND_URL is not configured")
        return

    login_url = f"{BACKEND_URL}/auth/login?origin={FRONTEND_URL}&return_mode=redirect"

    st.link_button(
        "Sign in with GitHub",
        login_url,
        use_container_width=False,
    )


# -------------------------------------------------
# Debug helpers (explicit use only)
# -------------------------------------------------
def render_auth_debug():
    """
    Optional developer-only debug panel.
    Call explicitly from a page or sidebar.
    """
    with st.expander("🔍 Auth Debug (developers)", expanded=False):
        st.write("Session state:")
        st.json({
            "auth_source": st.session_state.get(AUTH_SOURCE_KEY),
            "has_token": bool(st.session_state.get(TOKEN_KEY)),
        })

        st.write("Auth log:")
        st.json(st.session_state.get(AUTH_LOG_KEY, []))


def call_me():
    """
    Debug helper: call backend /me endpoint.
    """
    token = get_token()
    if not token:
        return None

    resp = requests.get(
        f"{BACKEND_URL}/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )

    if resp.status_code == 200:
        return resp.json()

    return {
        "error": resp.status_code,
        "text": resp.text,
    }


# -------------------------------------------------
# Public API
# -------------------------------------------------
__all__ = [
    "get_token",
    "is_authenticated",
    "clear_auth",
    "handle_callback",
    "login_button",
    "render_auth_debug",
    "call_me",
]
