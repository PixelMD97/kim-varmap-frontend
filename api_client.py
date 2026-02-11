import os
import requests
import streamlit as st


# -------------------------------------------------
# Configuration
# -------------------------------------------------
BASE_URL = os.getenv(
    "KIM_API_BASE_URL",
    "http://localhost:8000"
).rstrip("/")

TIMEOUT_SECONDS = 15


# -------------------------------------------------
# Internal helpers
# -------------------------------------------------
class ApiError(RuntimeError):
    pass


def _get_token():
    return st.session_state.get("access_token")


def _headers():
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    token = _get_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers


def _handle_response(response: requests.Response):
    if response.status_code >= 400:
        try:
            detail = response.json()
        except Exception:
            detail = response.text
        raise ApiError(f"{response.status_code}: {detail}")

    if not response.content:
        return None

    return response.json()


def _get(path: str):
    r = requests.get(
        f"{BASE_URL}{path}",
        headers=_headers(),
        timeout=TIMEOUT_SECONDS,
    )
    return _handle_response(r)


def _post(path: str, payload: dict):
    r = requests.post(
        f"{BASE_URL}{path}",
        json=payload,
        headers=_headers(),
        timeout=TIMEOUT_SECONDS,
    )
    return _handle_response(r)


def _patch(path: str, payload: dict):
    r = requests.patch(
        f"{BASE_URL}{path}",
        json=payload,
        headers=_headers(),
        timeout=TIMEOUT_SECONDS,
    )
    return _handle_response(r)


def _delete(path: str):
    r = requests.delete(
        f"{BASE_URL}{path}",
        headers=_headers(),
        timeout=TIMEOUT_SECONDS,
    )
    return _handle_response(r)


# -------------------------------------------------
# Project APIs
# -------------------------------------------------
def create_project(name: str, display_name: str, collaborators: list[str]):
    payload = {
        "name": name,
        "display_name": display_name,
        "allowed_users": collaborators,
    }

    try:
        return _post("/projects", payload)
    except ApiError as e:
        if "already exists" in str(e):
            return get_project(name)
        raise


def list_projects():
    return _get("/projects") or []


def get_project(name: str):
    return _get(f"/projects/{name}")


def update_project_settings(project: str, settings: dict):
    return _patch(
        f"/projects/{project}/config",
        {"settings": settings},
    )


# -------------------------------------------------
# Mapping APIs
# -------------------------------------------------
def fetch_base_mapping(project: str):
    return _get(f"/projects/{project}/mappings") or []


def create_mapping(project: str, payload: dict):
    return _post(f"/projects/{project}/mappings", payload)


def delete_mapping(project: str, mapping_id: str):
    _delete(f"/projects/{project}/mappings/{mapping_id}")
