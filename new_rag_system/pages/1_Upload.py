import streamlit as st
import requests
from typing import List, Optional
import datetime

st.set_page_config(page_title="Upload Documents", layout="wide")

API_BASE_URL = "http://127.0.0.1:8000"

def get_categories(token: str) -> List[dict]:
    """
    Fetches all available categories from the backend API.
    Requires an authentication token.
    """
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE_URL}/categories/", headers=headers)
    response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
    return response.json()

def create_new_category(token: str, category_name: str) -> dict:
    """
    Sends a request to the backend to create a new category.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {"name": category_name}
    response = requests.post(f"{API_BASE_URL}/categories/", json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

def upload_files(token: str, files, expires_at: Optional[str] = None, category_ids: Optional[List[int]] = None):
    """
    Uploads files to the backend API, optionally assigning them to categories
    and setting an expiration date.
    """
    headers = {"Authorization": f"Bearer {token}"}
    file_list = [("files", (file.name, file, file.type)) for file in files]

    data = {}
    if expires_at:
        data["expires_at"] = expires_at
    if category_ids:
        # FastAPI expects lists as multiple form fields with the same name
        # requests library handles this correctly when 'data' is a dict with list values
        data["category_ids"] = category_ids

    response = requests.post(
        f"{API_BASE_URL}/documents/upload",
        files=file_list,
        data=data,
        headers=headers
    )
    response.raise_for_status()
    return response.json()


st.title("Upload New Documents")

if 'token' not in st.session_state or st.session_state.token is None:
    st.warning("Please log in to upload documents.")
else:
    try:
        # Section to create new categories
        st.subheader("Create New Category")
        with st.form("create_category_form", clear_on_submit=True):
            new_category_name = st.text_input("New Category Name", help="Enter a name for a new category.")
            create_category_submitted = st.form_submit_button("Create Category")

            if create_category_submitted and new_category_name:
                with st.spinner(f"Creating category '{new_category_name}'..."):
                    try:
                        created_category = create_new_category(st.session_state.token, new_category_name)
                        st.success(f"Category '{created_category['name']}' created successfully!")
                        # Rerun to refresh the category list in the upload form below
                        st.rerun()
                    except requests.exceptions.RequestException as e:
                        st.error(f"Failed to create category: {e}")
                        if e.response is not None:
                            try:
                                error_detail = e.response.json().get('detail', 'No additional detail provided.')
                                st.error(f"Server response: {error_detail}")
                            except requests.exceptions.JSONDecodeError:
                                st.error(f"Server returned non-JSON response for category creation: {e.response.text}")
            elif create_category_submitted and not new_category_name:
                st.warning("Please enter a category name.")

        st.markdown("---") # Separator

        st.subheader("Upload Documents")
        # Load categories from the backend for the upload form
        with st.spinner("Loading categories..."):
            categories = get_categories(st.session_state.token)
            category_map = {cat['name']: cat['id'] for cat in categories}

        with st.form("upload_form", clear_on_submit=True):
            uploaded_files = st.file_uploader(
                "Choose one or more files",
                type=["pdf", "docx", "txt"],
                accept_multiple_files=True
            )

            # Display multiselect for categories
            if not categories:
                st.info("No categories available yet. Create one above to get started!")
                selected_categories = []
            else:
                selected_categories = st.multiselect(
                    "Assign to Categories (Optional)",
                    options=list(category_map.keys()),
                    help="Select existing categories to associate with the uploaded documents."
                )

            expires_at_date = st.date_input("Expiration Date (Optional)", value=None)

            submitted = st.form_submit_button("Upload")

            if submitted:
                if uploaded_files:
                    selected_category_ids = [category_map[name] for name in selected_categories]

                    expires_at_iso = expires_at_date.isoformat() if expires_at_date else None

                    with st.spinner("Uploading and processing files..."):
                        upload_files(
                            st.session_state.token,
                            uploaded_files,
                            expires_at_iso,
                            selected_category_ids
                        )
                    st.success(f"{len(uploaded_files)} file(s) uploaded successfully!")
                else:
                    st.error("Please select at least one file to upload.")

    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while communicating with the API: {e}")
        if e.response is not None:
            try:
                error_detail = e.response.json().get('detail', 'No additional detail provided by server.')
                st.error(f"Server response detail: {error_detail}")
            except requests.exceptions.JSONDecodeError:
                st.error(f"Server returned non-JSON response: {e.response.text}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

