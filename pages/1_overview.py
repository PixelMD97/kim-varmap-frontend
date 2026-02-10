import streamlit as st

from ui_stepper import render_stepper
from auth_ui import render_auth_status
from api_client import create_project, list_projects, get_project


# -------------------------------------------------
# Page setup
# -------------------------------------------------
render_auth_status()

st.set_page_config(
    page_title="KIM VarMap – Overview",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

render_stepper(current_step=0)


# -------------------------------------------------
# Header
# -------------------------------------------------
st.title("KIM VarMap")
st.caption(
    "A lightweight tool to browse, select, and export clinical variables "
    "with the corresponding EPIC/PDMS mapping."
)

st.markdown("### Project")


# -------------------------------------------------
# Project mode selection
# -------------------------------------------------
project_mode = st.radio(
    "Project mode",
    options=["Create new project", "Use existing project"],
    horizontal=True,
)

st.session_state["project_mode"] = project_mode


# -------------------------------------------------
# Helpers
# -------------------------------------------------
def _parse_emails(raw: str) -> list[str]:
    return [e.strip() for e in raw.split(",") if e.strip()]


# -------------------------------------------------
# EXISTING PROJECT PATH
# -------------------------------------------------
if project_mode == "Use existing project":
    try:
        projects = list_projects()
    except Exception as e:
        st.error(f"Failed to load projects: {e}")
        st.stop()

    if not projects:
        st.info("You do not have access to any existing projects yet.")
        st.stop()

    project_lookup = {
        f"{p['display_name']} ({p['name']})": p["name"]
        for p in projects
    }

    selected_label = st.selectbox(
        "Select a project",
        options=list(project_lookup.keys()),
    )

    selected_project = project_lookup[selected_label]

    st.markdown("---")

    if st.button("Continue →", use_container_width=True):
        try:
            project = get_project(selected_project)
            st.session_state["project"] = project["name"]

            st.success(f"Project '{project['display_name']}' loaded.")
            st.switch_page("pages/2_data_source.py")

        except Exception as e:
            st.error(f"Failed to load project: {e}")

    st.stop()


# -------------------------------------------------
# NEW PROJECT PATH (your original logic)
# -------------------------------------------------
st.markdown("### Project information")

left, right = st.columns([6, 1])

with left:
    project_name_input = st.text_input(
        "Project name",
        value=st.session_state.get("project_meta", {}).get("project_name", ""),
        key="project_name_input",
        placeholder="e.g., TEST STUDY …",
    )

    owner_email_input = st.text_input(
        "Your email",
        value=st.session_state.get("project_meta", {}).get("owner_email", ""),
        key="owner_email_input",
        placeholder="firstname.lastname@insel.ch",
        help="Primary contact person for this project",
    )

    collaborators_input = st.text_area(
        "Additional collaborators (optional)",
        value=", ".join(
            st.session_state.get("project_meta", {}).get("collaborators", [])
        ),
        key="collaborators_input",
        placeholder="email1@insel.ch, email2@insel.ch",
        help="Comma-separated list of collaborators invited to work on this project",
    )

with right:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    if project_name_input.strip():
        st.markdown(
            "<div style='text-align:right; color: rgba(49,51,63,0.65); "
            "font-size: 0.95rem;'>✓</div>",
            unsafe_allow_html=True,
        )


if project_name_input.strip():
    st.session_state["project_meta"] = {
        "project_name": project_name_input.strip(),
        "owner_email": owner_email_input.strip(),
        "collaborators": _parse_emails(collaborators_input),
    }


# -------------------------------------------------
# Informational text (unchanged)
# -------------------------------------------------
st.markdown("### How it works")
st.markdown(
    """
1. **Data source** – Choose whether you want to load the base mapping table
   (standard) and optionally upload your own files to work on.
2. **Choose variables** – Browse or search the complete available list of
   variables and select the variables you need.
3. **Export** – Review your selection and download as a CSV.
"""
)

st.markdown("---")


# -------------------------------------------------
# START → create new project
# -------------------------------------------------
if st.button("Start →", use_container_width=True):
    meta = st.session_state.get("project_meta")

    if not meta or not meta.get("project_name"):
        st.error("Please enter a project name.")
        st.stop()

    try:
        project = create_project(
            name=meta["project_name"],
            display_name=meta["project_name"],
            collaborators=meta.get("collaborators", []),
        )

        st.session_state["project"] = project["name"]

        st.success(f"Project '{project['display_name']}' created.")
        st.switch_page("pages/2_data_source.py")

    except Exception as e:
        st.error(f"Failed to create project: {e}")
