import traceback
import streamlit as st

from ui_stepper import render_stepper, render_bottom_nav
from auth_ui import render_auth_status
from api_client import update_project_settings


# -------------------------------------------------
# CONFIG
# -------------------------------------------------

DEBUG = True  # 🔁 Turn off in production


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

choice = st.radio(
    "Available source",
    options=["Both", "EPIC", "PDMS"],
    index=["Both", "EPIC", "PDMS"].index(
        st.session_state.get("source_filter", "Both")
    ),
)

st.session_state["source_filter"] = choice


# -------------------------------------------------
# SAVE TO BACKEND
# -------------------------------------------------

def map_choice_to_source_systems(choice: str):
    if choice == "Both":
        return ["EPIC", "PDMS"]
    if choice == "EPIC":
        return ["EPIC"]
    if choice == "PDMS":
        return ["PDMS"]
    return []

payload = {
    "source_systems": map_choice_to_source_systems(choice)
}

if DEBUG:
    with st.expander("🔍 DEBUG – Outgoing request", expanded=False):
        st.write("Project:", project)
        st.write("Payload:", payload)

try:
    response = update_project_settings(project, payload)

    if DEBUG:
        with st.expander("🔍 DEBUG – Backend response", expanded=False):
            st.write(response)

except Exception as e:
    st.error("❌ Failed to save selection")

    if DEBUG:
        with st.expander("🔥 DEBUG – Full error trace", expanded=True):
            st.write("Project:", project)
            st.write("Payload:", payload)
            st.code(traceback.format_exc())

    st.stop()



# -------------------------------------------------
# NAVIGATION
# -------------------------------------------------

st.markdown("---")
render_bottom_nav(current_step=1)
