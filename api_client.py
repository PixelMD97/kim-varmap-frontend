import os
import requests
import streamlit as st


# -------------------------------------------------
# Base config
# -------------------------------------------------

def _base_url():
    return os.getenv(
        "KIM_API_BASE_URL",
        "https://2025varmapbackend-adgyb5eqghc6bzay.westeurope-01.azurewebsites.net"
    ).rstrip("/")


def _headers():
    token = st.session_state.get("access_token")
    if not token:
        raise RuntimeError("Not authenticated")

    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def _get(path):
    r = requests.get(f"{_base_url()}{path}", headers=_headers())
    r.raise_for_status()
    return r.json() if r.content else None


def _post(path, payload):
    r = requests.post(f"{_base_url()}{path}", json=payload, headers=_headers())
    r.raise_for_status()
    return r.json() if r.content else None


def _patch(path, payload):
    r = requests.patch(f"{_base_url()}{path}", json=payload, headers=_headers())
    r.raise_for_status()
    return r.json() if r.content else None


def _put(path, payload):
    r = requests.put(f"{_base_url()}{path}", json=payload, headers=_headers())
    r.raise_for_status()
    return r.json() if r.content else None


def _delete(path):
    r = requests.delete(f"{_base_url()}{path}", headers=_headers())
    r.raise_for_status()


# -------------------------------------------------
# Projects
# -------------------------------------------------

def list_projects():
    return _get("/projects")


def create_project(name, display_name=None, collaborators=None):
    payload = {
        "name": name,
        "display_name": display_name,
        "allowed_users": collaborators or [],
    }
    return _post("/projects", payload)


def get_project(name):
    return _get(f"/projects/{name}")


def update_project_settings(project, settings: dict):
    # IMPORTANT: correct backend route
    return _patch(f"/projects/{project}/config", {"settings": settings})


# -------------------------------------------------
# Mappings
# -------------------------------------------------

def fetch_base_mapping(project):
    return _get(f"/projects/{project}/mappings")


def save_all_mappings(project, mappings):
    return _put(f"/projects/{project}/mappings/batch", mappings)


def create_mapping(project, payload):
    return _post(f"/projects/{project}/mappings", payload)


def update_mapping(project, mapping_id, payload):
    return _put(f"/projects/{project}/mappings/{mapping_id}", payload)


def delete_mapping(project, mapping_id):
    _delete(f"/projects/{project}/mappings/{mapping_id}")
