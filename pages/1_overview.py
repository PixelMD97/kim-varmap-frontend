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
def _parse_usernames(raw: str) -> list[str]:
    return [u.strip() for u in raw.split(",") if u.strip()]


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
        f"{p.get('name')} {'(default)' if p.get('default') else ''}".strip(): p.get("name")
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

            # ✅ Always set both project + project_meta
            st.session_state["project"] = project["name"]

            st.session_state["project_meta"] = {
                "project_name": project.get("display_name") or project["name"],
                "owner_email": "",
                "collaborators": project.get("allowed_users", []),
            }

            st.success(f"Project '{project.get('display_name') or project['name']}' loaded.")
            st.switch_page("pages/2_system_selection.py")

        except Exception as e:
            st.error(f"Failed to load project: {e}")

    st.stop()


# -------------------------------------------------
# NEW PROJECT PATH
# -------------------------------------------------
st.markdown("### Project information")

left, right = st.columns([6, 1])

with left:
    project_name_input = st.text_input(
        "Project name",
        value=st.session_state.get("project_meta", {}).get("project_name", ""),
        key="project_name_input",
        placeholder="e.g., ICU_STUDY_2026",
    )

    collaborators_input = st.text_area(
        "Additional collaborators (GitHub usernames)",
        value=", ".join(
            st.session_state.get("project_meta", {}).get("collaborators", [])
        ),
        key="collaborators_input",
        placeholder="username1, username2",
        help="Comma-separated list of GitHub usernames allowed to edit this project",
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
        "collaborators": _parse_usernames(collaborators_input),
    }


# -------------------------------------------------
# Informational text
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
# CREATE NEW PROJECT
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
#            from_project="default",  # copy default mappings
        )

        st.session_state["project"] = project["name"]

        st.session_state["project_meta"] = {
            "project_name": project.get("display_name") or project["name"],
            "collaborators": project.get("allowed_users", []),
        }

        st.success(f"Project '{project.get('display_name') or project['name']}' created.")
        st.switch_page("pages/2_system_selection.py")

    except Exception as e:
        st.error(f"Failed to create project: {e}")
