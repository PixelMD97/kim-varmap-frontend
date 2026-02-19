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
        raise RuntimeError("Not authenticated (no access_token in session_state)")

    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


# -------------------------------------------------
# CORE DEBUG REQUEST WRAPPER
# -------------------------------------------------

def _request(method: str, path: str, payload=None):
    url = f"{_base_url()}{path}"
    headers = _headers()

    # ---- DEBUG: Outgoing request ----
    print("\n" + "=" * 80)
    print(f"[API REQUEST] {method} {url}")
    print("Headers:", {k: v if k != "Authorization" else "Bearer ***" for k, v in headers.items()})
    if payload is not None:
        print("Payload:", payload)

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=payload if payload is not None else None,
        )

        print(f"[API RESPONSE] Status: {response.status_code}")

        # Try printing JSON body
        try:
            body = response.json()
        except Exception:
            body = response.text

        print("Response Body:", body if len(str(body)) < 2000 else str(body)[:2000] + " ...")

        response.raise_for_status()

        return body if response.content else None

    except requests.HTTPError as e:
        print("❌ HTTP ERROR")
        print("Status:", response.status_code)
        print("Response Text:", response.text)
        raise

    except Exception as e:
        print("❌ UNEXPECTED ERROR:", e)
        raise

    finally:
        print("=" * 80 + "\n")


# -------------------------------------------------
# Thin wrappers
# -------------------------------------------------

def _get(path):
    return _request("GET", path)


def _post(path, payload):
    return _request("POST", path, payload)


def _patch(path, payload):
    return _request("PATCH", path, payload)


def _put(path, payload):
    return _request("PUT", path, payload)


def _delete(path):
    return _request("DELETE", path)


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
    # backend route: PATCH /projects/{project}/config
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
    return _delete(f"/projects/{project}/mappings/{mapping_id}")
