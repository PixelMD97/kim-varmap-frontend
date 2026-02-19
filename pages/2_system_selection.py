import streamlit as st

from ui_stepper import render_stepper, render_bottom_nav
from auth_ui import render_auth_status
from api_client import update_project_settings
from project_guard import require_project


if "project" not in st.session_state:
    st.switch_page("pages/1_overview.py")
    st.stop()


# -------------------------------------------------
# Page setup
# -------------------------------------------------
render_auth_status()

st.set_page_config(
    page_title="KIM VarMap – Data source system",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_stepper(current_step=1)


# -------------------------------------------------
# Safety: require project
# -------------------------------------------------
project = st.session_state.get("project")
if not project:
    st.error("No project selected. Please start from the Overview page.")
    st.stop()


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
# Persist (single source of truth)
# -------------------------------------------------
st.session_state["source_filter"] = choice

try:
    update_project_settings(
        project=project,
        settings={"source_filter": choice},
    )
except Exception as e:
    st.error(f"Failed to save source selection: {e}")


render_bottom_nav(current_step=2)
