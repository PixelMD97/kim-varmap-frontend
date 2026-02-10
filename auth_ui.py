# auth_ui.py
import streamlit as st
from iam_workflow import get_token


import streamlit as st

def render_auth_status():
    st.session_state.setdefault("user", "demo-user")
    st.success("✅ Logged in")
    st.caption("User: demo-user")

