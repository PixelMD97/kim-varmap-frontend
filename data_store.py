import pandas as pd
import streamlit as st

from api_client import fetch_base_mapping


# -----------------------------------------
# Core columns expected by frontend
# -----------------------------------------
EXPECTED_COLUMNS = [
    "Organ System",
    "Group",
    "Variable",
    "EPIC ID",
    "PDMS ID",
    "Unit",
]


# -----------------------------------------
# Convert backend mapping JSON -> DataFrame
# -----------------------------------------
def backend_mappings_to_df(mappings: list[dict]) -> pd.DataFrame:
    """
    Convert backend JSON schema to frontend tabular structure.
    """

    rows = []

    for m in mappings:
        classification = m.get("classification", {})
        path = classification.get("path", [])

        organ_system = path[0] if len(path) > 0 else "General"
        group = path[1] if len(path) > 1 else "General"

        epic_id = ""
        pdms_id = ""

        for src in m.get("source", []):
            system = src.get("system", "").upper()
            variable = src.get("variable", "")

            if system == "EPIC":
                epic_id = variable
            elif system == "PDMS":
                pdms_id = variable

        rows.append({
            "Organ System": organ_system,
            "Group": group,
            "Variable": m.get("name", ""),
            "EPIC ID": epic_id,
            "PDMS ID": pdms_id,
            "Unit": m.get("unit", ""),
            "__row_key__": m.get("id"),
        })

    df = pd.DataFrame(rows)

    # ensure structure
    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    return df


# -----------------------------------------
# Main entry point for UI
# -----------------------------------------
def get_master_df() -> pd.DataFrame:
    """
    Single source of truth.

    Loads mappings from backend and converts to frontend format.
    """

    project = st.session_state.get("project")
    if not project:
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

    mappings = fetch_base_mapping(project)

    if mappings is None or len(mappings) == 0:
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

    df = backend_mappings_to_df(mappings)

    # -------------------------
    # Apply EPIC / PDMS filter
    # -------------------------
    source_filter = st.session_state.get("source_filter", "Both")

    if source_filter == "EPIC":
        df = df[df["EPIC ID"].astype(str).str.strip() != ""]
    elif source_filter == "PDMS":
        df = df[df["PDMS ID"].astype(str).str.strip() != ""]

    return df.reset_index(drop=True)
