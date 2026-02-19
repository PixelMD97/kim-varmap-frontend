import pandas as pd
import streamlit as st

from api_client import fetch_base_mapping

EXPECTED_COLUMNS = [
    "Organ System",
    "Group",
    "Variable",
    "EPIC ID",
    "PDMS ID",
    "Unit",
]


@st.cache_data(show_spinner=False)
def load_project_mappings(project: str) -> list[dict]:
    return fetch_base_mapping(project) or []


def backend_mappings_to_df(mappings: list[dict]) -> pd.DataFrame:
    rows = []
    mapping_lookup = {}

    for m in mappings:
        mapping_id = m.get("id")
        classification = m.get("classification") or {}
        path = classification.get("path") or []

        organ_system = path[0] if len(path) > 0 else "General"
        group = path[1] if len(path) > 1 else "General"

        epic_id = ""
        pdms_id = ""

        for src in m.get("source") or []:
            system = (src.get("system") or "").upper()
            variable = src.get("variable") or ""

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
            "__row_key__": mapping_id,
        })

        mapping_lookup[mapping_id] = m

    df = pd.DataFrame(rows)

    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    st.session_state["mapping_lookup"] = mapping_lookup

    return df


def get_master_df() -> pd.DataFrame:
    project = st.session_state.get("project")
    if not project:
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

    mappings = load_project_mappings(project)

    if not mappings:
        df = pd.DataFrame(columns=EXPECTED_COLUMNS + ["__row_key__"])
        return df


    df = backend_mappings_to_df(mappings)

    source_filter = st.session_state.get("source_filter", "Both")

    if source_filter == "EPIC":
        df = df[df["EPIC ID"].astype(str).str.strip() != ""]
    elif source_filter == "PDMS":
        df = df[df["PDMS ID"].astype(str).str.strip() != ""]

    return df.reset_index(drop=True)
