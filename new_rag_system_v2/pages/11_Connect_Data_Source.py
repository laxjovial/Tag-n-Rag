import streamlit as st
import requests
from app.utils import check_auth

# --- Authentication Check ---
check_auth("Connect Data Source")

# --- Page Configuration ---
st.set_page_config(page_title="Connect Data Source", layout="wide")

# --- API Configuration ---
API_BASE_URL = "http://127.0.0.1:8000"

# --- Helper Functions ---
def get_auth_headers():
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"}

@st.cache_data(ttl=10)
def get_user_connection_status():
    response = requests.get(f"{API_BASE_URL}/user/me", headers=get_auth_headers())
    response.raise_for_status()
    return response.json().get("has_google_credentials", False)

@st.cache_data(ttl=60)
def list_gdrive_files(folder_id='root'):
    params = {"folder_id": folder_id}
    response = requests.get(f"{API_BASE_URL}/gdrive/files", headers=get_auth_headers(), params=params)
    response.raise_for_status()
    return response.json()

def ingest_from_gdrive(file_ids: list[str]):
    """Triggers the ingestion of selected Google Drive files."""
    payload = {"file_ids": file_ids}
    response = requests.post(f"{API_BASE_URL}/gdrive/ingest", json=payload, headers=get_auth_headers())
    response.raise_for_status()
    return response.json()

# --- UI Rendering ---
st.title("Connect Your Data Sources")

try:
    is_connected = get_user_connection_status()

    tab1, tab2 = st.tabs(["Connection Status", "Upload from Google Drive"])

    with tab1:
        st.subheader("Google Drive Connection")
        if is_connected:
            st.success("You have successfully connected your Google Drive account.")
            if st.button("Disconnect Google Drive"):
                st.warning("Disconnect functionality is not yet implemented.")
        else:
            st.info("You have not connected your Google Drive account yet.")
            st.link_button("Connect to Google Drive", f"{API_BASE_URL}/auth/google/login")

    with tab2:
        if not is_connected:
            st.info("Please connect your Google Drive account in the 'Connection Status' tab first.")
        else:
            st.subheader("Select Files to Upload to Server")

            files = list_gdrive_files()

            if not files:
                st.write("No files found in your Google Drive's root folder.")
            else:
                with st.form("ingest_form"):
                    selected_files = []
                    for file in files:
                        is_folder = file['mimeType'] == 'application/vnd.google-apps.folder'
                        icon = "📁" if is_folder else "📄"
                        label = f"{icon} {file['name']}"

                        if not is_folder:
                            if st.checkbox(label, key=file['id']):
                                selected_files.append(file['id'])
                        else:
                            st.write(label)

                    submitted = st.form_submit_button("Upload Selected Files")
                    if submitted:
                        if selected_files:
                            with st.spinner("Uploading files from your Drive... This may take a moment."):
                                ingested_docs = ingest_from_gdrive(selected_files)
                                st.success(f"Successfully uploaded {len(ingested_docs)} file(s)!")
                                st.write("You can now view them on the 'View Documents' page.")
                                st.cache_data.clear()
                        else:
                            st.warning("Please select at least one file to upload.")

except requests.exceptions.RequestException as e:
    st.error(f"An API error occurred: {e}")
except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
