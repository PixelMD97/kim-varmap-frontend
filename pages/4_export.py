import pandas as pd
import streamlit as st
from datetime import datetime

from ui_stepper import render_stepper, render_bottom_nav
from auth_ui import render_auth_status
from data_store import get_master_df
from api_client import create_mapping


if "project" not in st.session_state:
    st.switch_page("pages/1_overview.py")
    st.stop()


# -------------------------------------------------
# Page setup
# -------------------------------------------------
render_auth_status()

st.set_page_config(
    page_title="KIM VarMap – Export",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_stepper(current_step=4)


# -------------------------------------------------
# Safety: require project
# -------------------------------------------------
project = st.session_state.get("project")
if not project:
    st.error("No project selected. Please start from the Overview page.")
    st.stop()


# -------------------------------------------------
# Header
# -------------------------------------------------
st.title("Export")
st.markdown("Review your selected variables and download them as a CSV.")

project_name = (
    st.session_state.get("project_meta", {})
    .get("project_name", "")
    .strip()
)

if project_name:
    st.markdown(f"Project: **{project_name}**")


# -------------------------------------------------
# Load state
# -------------------------------------------------
granularity_rows = st.session_state.get("granularity_rows", [])

if not granularity_rows:
    st.info("No variables selected yet. Go back to **Choose variables**.")
    render_bottom_nav(current_step=4)
    st.stop()

gran_df = pd.DataFrame(granularity_rows)
master_df = get_master_df()


# -------------------------------------------------
# Merge granularity + master data
# -------------------------------------------------
export_df = gran_df.merge(
    master_df,
    how="left",
    left_on="row_key",
    right_on="__row_key__",
)


# -------------------------------------------------
# Origin & inferred Source
# -------------------------------------------------
export_df["Origin"] = "Base"

def infer_source(row):
    epic = str(row.get("EPIC ID", "")).strip()
    pdms = str(row.get("PDMS ID", "")).strip()

    if epic and pdms:
        return "Both"
    if epic:
        return "EPIC"
    if pdms:
        return "PDMS"
    return ""

export_df["Source"] = export_df.apply(infer_source, axis=1)


# -------------------------------------------------
# Final display table
# -------------------------------------------------
DISPLAY_COLUMNS = [
    "Variable",
    "Organ System",
    "Group",
    "Source",
    "EPIC ID",
    "PDMS ID",
    "Unit",
    "Origin",
    "Summary",
    "Time basis",
]

for col in DISPLAY_COLUMNS:
    if col not in export_df.columns:
        export_df[col] = ""

table_df = export_df[DISPLAY_COLUMNS].copy()
table_df.insert(0, "Delete", False)

st.subheader("Selected variables")

edited = st.data_editor(
    table_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Delete": st.column_config.CheckboxColumn(""),
        "Variable": st.column_config.TextColumn(disabled=True),
        "Organ System": st.column_config.TextColumn(disabled=True),
        "Group": st.column_config.TextColumn(disabled=True),
        "Source": st.column_config.TextColumn(disabled=True),
        "EPIC ID": st.column_config.TextColumn(disabled=True),
        "PDMS ID": st.column_config.TextColumn(disabled=True),
        "Unit": st.column_config.TextColumn(disabled=True),
        "Origin": st.column_config.TextColumn(disabled=True),
        "Summary": st.column_config.TextColumn(disabled=True),
        "Time basis": st.column_config.TextColumn(disabled=True),
    },
)


# -------------------------------------------------
# Delete selected rows
# -------------------------------------------------
if st.button("🗑 Delete selected"):
    keep_mask = ~edited["Delete"]
    kept = gran_df.loc[keep_mask.values].copy()

    st.session_state["granularity_rows"] = kept.to_dict(orient="records")
    st.success("Selected rows removed.")
    st.rerun()


# -------------------------------------------------
# CSV export
# -------------------------------------------------
csv_df = export_df[DISPLAY_COLUMNS].copy()

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
safe_project = (project_name or project).replace(" ", "_").lower()

csv_bytes = csv_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download CSV",
    data=csv_bytes,
    file_name=f"variablemapping_{safe_project}_{timestamp}.csv",
    mime="text/csv",
)


# -------------------------------------------------
# Add variable (backend-driven)
# -------------------------------------------------
st.markdown("---")
st.subheader("Add a variable")

COMMON_UNITS = [
    "", "mmHg", "bpm", "%", "°C", "kg", "g/L",
    "mg/L", "mmol/L", "mL", "L/min", "score", "Other"
]

with st.form("add_variable_form", clear_on_submit=True):
    variable = st.text_input("Variable *", placeholder="e.g. Creatinine")
    organ_system = st.text_input("Organ system", placeholder="e.g. Renal")
    group = st.text_input("Group", placeholder="e.g. Labs")

    epic_id = st.text_input("EPIC ID")
    pdms_id = st.text_input("PDMS ID")

    unit_choice = st.selectbox("Unit", options=COMMON_UNITS)
    unit_other = ""
    if unit_choice == "Other":
        unit_other = st.text_input("Other unit")

    submitted = st.form_submit_button("Add variable")


if submitted:
    if not variable.strip():
        st.error("Variable name is required.")
        st.stop()

    if not epic_id.strip() and not pdms_id.strip():
        st.error("Please provide at least one identifier (EPIC ID or PDMS ID).")
        st.stop()

    unit_clean = unit_other.strip() if unit_choice == "Other" else unit_choice

    payload = {
        "name": variable.strip(),
        "source": [],
        "status": "active",
        "unit": unit_clean,
        "classification": {
            "path": [
                organ_system.strip() or "General",
                group.strip() or "General",
            ]
        }
    }

    if epic_id.strip():
        payload["source"].append({
            "system": "EPIC",
            "variable": epic_id.strip()
        })

    if pdms_id.strip():
        payload["source"].append({
            "system": "PDMS",
            "variable": pdms_id.strip()
        })

    try:
        create_mapping(project, payload)

        # Clear Streamlit cache so new mapping appears
        st.cache_data.clear()

        st.success("Variable added successfully.")
        st.rerun()

    except Exception as e:
        st.error(f"Failed to create mapping: {e}")


st.markdown("---")
render_bottom_nav(current_step=4)
