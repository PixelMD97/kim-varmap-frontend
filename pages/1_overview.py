import streamlit as st

from ui_stepper import render_stepper
from auth_ui import render_auth_status
from api_client import create_project


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

st.markdown("### Project information")


# -------------------------------------------------
# Input fields
# -------------------------------------------------
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


# -------------------------------------------------
# Helpers
# -------------------------------------------------
def _parse_emails(raw: str) -> list[str]:
    return [e.strip() for e in raw.split(",") if e.strip()]


# -------------------------------------------------
# Persist local UX state (unchanged)
# -------------------------------------------------
if project_name_input.strip():
    st.session_state["project_meta"] = {
        "project_name": project_name_input.strip(),
        "owner_email": owner_email_input.strip(),
        "collaborators": _parse_emails(collaborators_input),
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

st.markdown("### What you get")
st.markdown(
    "- A clean CSV export of selected variables (with identifiers and metadata), "
    "named using your project and the export date."
)

st.markdown("---")

st.markdown(
    """
### Data usage & responsibilities

- Retrospective data analysis in a **datenschutzkonforme** manner
  and in compliance with applicable institutional and legal requirements.
- If you receive an IDS-C dataset based on this mapping, we ask you to
  help improve mappings and **return the final dataset or derived variable list**.
- All data processing complies with institutional DLF and data protection policies.
"""
)

st.markdown("---")


# -------------------------------------------------
# START → backend project creation
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

        # 🔐 canonical backend project anchor
        st.session_state["project"] = project["name"]

        st.success(f"Project '{project['display_name']}' ready.")
        st.switch_page("pages/2_data_source.py")

    except Exception as e:
        st.error(f"Failed to create project: {e}")
