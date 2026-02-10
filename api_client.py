import requests

BASE_URL = "http://localhost:8000"


def create_project(name, display_name, collaborators):
    payload = {
        "name": name,
        "display_name": display_name,
        "allowed_users": collaborators,
    }

    r = requests.post(f"{BASE_URL}/projects", json=payload)

    # project already exists → fetch it
    if r.status_code == 400 and "already exists" in r.text:
        r = requests.get(f"{BASE_URL}/projects/{name}")

    r.raise_for_status()
    return r.json()


def list_projects():
    r = requests.get(f"{BASE_URL}/projects")
    r.raise_for_status()
    return r.json()



def create_mapping(project, payload):
    r = requests.post(
        f"{BASE_URL}/projects/{project}/mappings", json=payload
    )
    r.raise_for_status()
    return r.json()


def delete_mapping(project, mapping_id):
    r = requests.delete(
        f"{BASE_URL}/projects/{project}/mappings/{mapping_id}"
    )
    r.raise_for_status()
