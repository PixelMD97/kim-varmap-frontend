import streamlit as st
from iam_workflow import (
    handle_callback,
    is_authenticated,
    login_button,
    call_me,
    clear_auth,
)

st.set_page_config(
    page_title="KIM VarMap",
    page_icon="🧠",
    layout="wide",
)

# -------------------------------------------------
# 1️⃣ Handle OAuth callback ONCE
# -------------------------------------------------
callback_hit = handle_callback()

# Optional dev debug
if st.session_state.get("debug", False):
    st.write("🧪 callback_hit =", callback_hit)
    st.write("🧪 session_state =", dict(st.session_state))

# -------------------------------------------------
# 2️⃣ If authenticated → go to app
# -------------------------------------------------
if is_authenticated():
    st.switch_page("pages/1_overview.py")

# -------------------------------------------------
# 3️⃣ Login screen (only if NOT authenticated)
# -------------------------------------------------
st.title("KIM VarMap")
st.caption(
    "A lightweight tool to browse, select, and export clinical variables "
    "with EPIC / PDMS mappings."
)

st.markdown("---")

st.markdown("### Welcome")
st.markdown("Please sign in with your GitHub account to continue.")

login_button()

st.markdown("---")

st.info(
    "You need a GitHub account with access to the KIM data mapping project."
)
