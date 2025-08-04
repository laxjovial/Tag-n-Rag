import streamlit as st
import requests

from src.frontend.utils import check_auth

from app.utils import check_auth


# --- Authentication Check ---
check_auth("Manage Mappings")

# --- Page Configuration ---
st.set_page_config(page_title="Manage Mappings", layout="wide")

# --- API Configuration ---
API_BASE_URL = "http://127.0.0.1:8000"

# --- Helper Functions ---
def get_auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

@st.cache_data(ttl=60)
def get_data():
    headers = get_auth_headers()
    cats_response = requests.get(f"{API_BASE_URL}/categories/", headers=headers)
    cats_response.raise_for_status()
    maps_response = requests.get(f"{API_BASE_URL}/mappings/", headers=headers)
    maps_response.raise_for_status()
    return {"categories": cats_response.json(), "mappings": maps_response.json()}

def create_mapping(category_id: int, folder_id: str, folder_name: str):
    payload = {"category_id": category_id, "folder_id": folder_id, "folder_name": folder_name}
    response = requests.post(f"{API_BASE_URL}/mappings/", json=payload, headers=get_auth_headers())
    response.raise_for_status()
    st.cache_data.clear()

def delete_mapping(mapping_id: int):
    response = requests.delete(f"{API_BASE_URL}/mappings/{mapping_id}", headers=get_auth_headers())
    response.raise_for_status()
    st.cache_data.clear()

# --- UI Rendering ---
st.title("Manage Google Drive Folder Mappings")
st.write("Map your app categories to Google Drive folders to enable 'read-on-the-fly' queries.")

try:
    with st.spinner("Loading categories and mappings..."):
        data = get_data()
        categories = data["categories"]
        mappings = data["mappings"]

    st.header("Existing Mappings")
    if not mappings:
        st.info("You have no folder mappings.")
    else:
        for mapping in mappings:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"Category **{mapping['category_name']}** is mapped to Google Drive folder **{mapping['folder_name']}** (`{mapping['folder_id']}`)")
            with col2:
                if st.button("Delete", key=f"del_map_{mapping['id']}", type="primary"):
                    delete_mapping(mapping['id'])
                    st.rerun()

    st.divider()

    st.header("Create New Mapping")
    unmapped_categories = [cat for cat in categories if cat['id'] not in [m['category_id'] for m in mappings]]
    if not unmapped_categories:
        st.warning("All your categories are already mapped. Create a new category to add a new mapping.")
    else:
        with st.form("create_mapping_form"):
            cat_map = {cat['name']: cat['id'] for cat in unmapped_categories}
            selected_cat_name = st.selectbox("Select Category to Map", list(cat_map.keys()))
            gdrive_folder_id = st.text_input("Google Drive Folder ID", help="Find this in the URL of your Google Drive folder.")
            gdrive_folder_name = st.text_input("Folder Name (for your reference)")

            if st.form_submit_button("Create Mapping"):
                if not all([selected_cat_name, gdrive_folder_id, gdrive_folder_name]):
                    st.error("Please fill out all fields.")
                else:
                    try:
                        create_mapping(cat_map[selected_cat_name], gdrive_folder_id, gdrive_folder_name)
                        st.success("Mapping created successfully!")
                        st.rerun()
                    except requests.exceptions.RequestException as e:
                        st.error(f"Failed to create mapping: {e.response.json().get('detail', e)}")

except requests.exceptions.RequestException as e:
    st.error(f"An API error occurred: {e}")
except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
