import os
import requests
import streamlit as st
import traceback

DEBUG = True


# -------------------------------------------------
# Base config
# -------------------------------------------------

def _base_url():
    return os.getenv(
        "KIM_API_BASE_URL",
        "https://2025varmapbackend-adgyb5eqghc6bzay.westeurope-01.azurewebsites.net"
    ).rstrip("/")


def _headers():
    token = st.session_state.get("access_token")
    if not token:
        raise RuntimeError("Not authenticated")

    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


# -------------------------------------------------
# CORE REQUEST WRAPPER
# -------------------------------------------------

def _request(method, path, payload=None):
    url = f"{_base_url()}{path}"
    headers = _headers()

    if DEBUG:
        with st.expander(f"🔍 DEBUG – {method} {path}", expanded=False):
            st.write("URL:", url)
            st.write("Method:", method)
            st.write("Has Authorization header:", "Authorization" in headers)
            if payload:
                st.write("Payload:", payload)

    try:
        r = requests.request(
            method=method,
            url=url,
            json=payload,
            headers=headers,
        )

        if DEBUG:
            with st.expander(f"📥 DEBUG – Response {r.status_code}", expanded=False):
                try:
                    st.write("Response JSON:", r.json())
                except Exception:
                    st.write("Raw response:", r.text)

        r.raise_for_status()

        return r.json() if r.content else None

    except Exception:
        if DEBUG:
            with st.expander("🔥 DEBUG – Exception Trace", expanded=True):
                st.code(traceback.format_exc())
        raise
