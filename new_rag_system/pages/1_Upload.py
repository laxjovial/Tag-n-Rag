import streamlit as st
import requests
from typing import List

st.set_page_config(page_title="Upload Documents", layout="wide")

API_BASE_URL = "http://localhost:8000"

def get_categories(token: str) -> List[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE_URL}/categories/", headers=headers)
    response.raise_for_status()
    return response.json()

def upload_files(token: str, files, expires_at=None, category_ids=None):
    headers = {"Authorization": f"Bearer {token}"}
    file_list = [("files", (file.name, file, file.type)) for file in files]
    data = {}
    if expires_at:
        data["expires_at"] = expires_at.isoformat()
    if category_ids:
        # FastAPI expects lists as multiple form fields with the same name
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
        with st.spinner("Loading categories..."):
            categories = get_categories(st.session_state.token)
            category_map = {cat['name']: cat['id'] for cat in categories}

        with st.form("upload_form", clear_on_submit=True):
            uploaded_files = st.file_uploader(
                "Choose one or more files",
                type=["pdf", "docx", "txt"],
                accept_multiple_files=True
            )

            selected_categories = st.multiselect(
                "Assign to Categories (Optional)",
                options=list(category_map.keys())
            )

            expires_at = st.date_input("Expiration Date (Optional)", value=None)

            submitted = st.form_submit_button("Upload")

            if submitted:
                if uploaded_files:
                    selected_category_ids = [category_map[name] for name in selected_categories]
                    with st.spinner("Uploading and processing files..."):
                        upload_files(
                            st.session_state.token,
                            uploaded_files,
                            expires_at,
                            selected_category_ids
                        )
                    st.success(f"{len(uploaded_files)} file(s) uploaded successfully!")
                else:
                    st.error("Please select at least one file to upload.")

    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
