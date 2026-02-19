import streamlit as st

from ui_stepper import render_stepper, render_bottom_nav
from auth_ui import render_auth_status
from api_client import update_project_settings

import requests
st.write(requests.get("https://2025varmapbackend-adgyb5eqghc6bzay.westeurope-01.azurewebsites.net/openapi.json").json())

from api_client import _get
st.write(_get("/whoami"))

# -------------------------------------------------
# Auth
# -------------------------------------------------
render_auth_status()

# -------------------------------------------------
# Page setup
# -------------------------------------------------
st.set_page_config(
    page_title="KIM VarMap – Data source system",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_stepper(current_step=1)

# -------------------------------------------------
# Require project
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

choice = st.radio(
    "Available source",
    options=["Both", "EPIC", "PDMS"],
    index=["Both", "EPIC", "PDMS"].index(
        st.session_state.get("source_filter", "Both")
    ),
)

# -------------------------------------------------
# Persist
# -------------------------------------------------
st.session_state["source_filter"] = choice

try:
    update_project_settings(
        project,
        {"source_filter": choice},
    )
except Exception as e:
    st.error(f"Failed to save selection: {e}")

st.markdown("---")
render_bottom_nav(current_step=1)
