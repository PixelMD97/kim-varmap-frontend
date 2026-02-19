import streamlit as st

from ui_stepper import render_stepper, render_bottom_nav
from auth_ui import render_auth_status


# -------------------------------------------------
# AUTH
# -------------------------------------------------

render_auth_status()


# -------------------------------------------------
# PAGE SETUP
# -------------------------------------------------

st.set_page_config(
    page_title="KIM VarMap – Data source system",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_stepper(current_step=1)


# -------------------------------------------------
# REQUIRE PROJECT
# -------------------------------------------------

if "project" not in st.session_state:
    st.switch_page("pages/1_overview.py")
    st.stop()

project = st.session_state["project"]


# -------------------------------------------------
# UI
# -------------------------------------------------

st.title("Data source system")

st.markdown(
    "Select which system(s) you want to extract variables from. "
    "This only affects visibility – data itself is not deleted."
)

st.caption(
    "You can change this later. All variables remain available in the background."
)


# -------------------------------------------------
# RADIO SELECTION
# -------------------------------------------------

choice = st.radio(
    "Available source",
    options=["Both", "EPIC", "PDMS"],
    index=["Both", "EPIC", "PDMS"].index(
        st.session_state.get("source_filter", "Both")
    ),
)

# -------------------------------------------------
# 🔥 IMPORTANT: ONLY STORE LOCALLY
# -------------------------------------------------

# ⬇️ This replaces backend PATCH completely
st.session_state["source_filter"] = choice


# -------------------------------------------------
# NAVIGATION
# -------------------------------------------------

st.markdown("---")
render_bottom_nav(current_step=1)
