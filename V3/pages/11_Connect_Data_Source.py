import streamlit as st
import requests
from src.frontend.utils import check_auth

# --- Authentication Check ---
check_auth("Manage Connections")

# --- Page Configuration ---
st.set_page_config(page_title="Manage Connections", layout="wide")

# --- API Configuration ---
API_BASE_URL = "http://127.0.0.1:8000"

# --- Helper Functions ---
def get_auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

@st.cache_data(ttl=30)
def get_connections():
    response = requests.get(f"{API_BASE_URL}/connections/", headers=get_auth_headers())
    response.raise_for_status()
    return response.json()

def delete_connection(connection_id: int):
    requests.delete(f"{API_BASE_URL}/connections/{connection_id}", headers=get_auth_headers()).raise_for_status()
    st.cache_data.clear()
    st.rerun()

def get_confluence_auth_url(site_url: str):
    response = requests.post(f"{API_BASE_URL}/auth/confluence/login", data={"site_url": site_url}, headers=get_auth_headers())
    response.raise_for_status()
    return response.json()['authorization_url']

# --- UI Rendering ---
st.title("Manage Your Data Source Connections")
st.write("Connect to external services to enable new ways of querying your data.")

AVAILABLE_SERVICES = {
    "google_drive": {"name": "Google Drive", "icon": "☁️", "login_path": "/auth/google/login"},
    "dropbox": {"name": "Dropbox", "icon": "📦", "login_path": "/auth/dropbox/login"},
    "onedrive": {"name": "Microsoft OneDrive", "icon": "📄", "login_path": "/auth/onedrive/login"},
    "confluence": {"name": "Atlassian Confluence", "icon": " Jira", "login_path": "/auth/confluence/login"},
    "google_keep": {"name": "Google Keep", "icon": "💡", "login_path": None},
}

try:
    connections = get_connections()
    connected_services = {conn['service_name'] for conn in connections}

    st.header("Your Connections")
    if not connections:
        st.info("You have not connected any external services yet.")
    else:
        for conn in connections:
            service_info = AVAILABLE_SERVICES.get(conn['service_name'], {"name": conn['service_name'], "icon": "🔗"})
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(f"{service_info['icon']} {service_info['name']}")
            with col2:
                if st.button("Delete", key=f"del_conn_{conn['id']}", type="primary"):
                    delete_connection(conn['id'])

    st.divider()

    st.header("Available Connections")
    for service_id, service_info in AVAILABLE_SERVICES.items():
        if service_id not in connected_services:
            with st.container(border=True):
                st.subheader(f"{service_info['icon']} {service_info['name']}")

                if service_id == "confluence":
                    with st.form(key="confluence_connect_form"):
                        site_url = st.text_input("Your Confluence Site URL (e.g., https://your-company.atlassian.net)")
                        if st.form_submit_button("Connect Confluence"):
                            if site_url:
                                auth_url = get_confluence_auth_url(site_url)
                                st.link_button("Proceed to Atlassian", auth_url)
                            else:
                                st.error("Please enter your Confluence site URL.")
                elif service_info['login_path']:
                    login_url = f"{API_BASE_URL}{service_info['login_path']}"
                    st.link_button(f"Connect {service_info['name']}", login_url)
                else:
                    st.button("Connect", disabled=True, help="This service does not have a public API and cannot be connected.")

except requests.exceptions.RequestException as e:
    st.error(f"An API error occurred: {e}")
except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
