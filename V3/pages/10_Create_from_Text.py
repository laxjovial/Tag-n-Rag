import streamlit as st
import requests
from typing import List

st.set_page_config(page_title="Create from Text", layout="wide")

API_BASE_URL = "http://localhost:8000"

def get_categories(token: str) -> List[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE_URL}/categories/", headers=headers)
    response.raise_for_status()
    return response.json()

def create_from_text(token: str, filename: str, content: str, category_ids: List[int] = None):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "filename": filename,
        "content": content,
        "category_ids": category_ids or []
    }
    response = requests.post(f"{API_BASE_URL}/documents/from_text", json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

st.title("Create a New Document from Text")

if 'token' not in st.session_state or st.session_state.token is None:
    st.warning("Please log in to create documents.")
else:
    try:
        with st.spinner("Loading categories..."):
            categories = get_categories(st.session_state.token)
            category_map = {cat['name']: cat['id'] for cat in categories}

        with st.form("create_from_text_form", clear_on_submit=True):
            filename = st.text_input("Enter a filename for your new document (e.g., 'My Notes')")
            content = st.text_area("Paste or type your text here", height=400)

            selected_categories = st.multiselect(
                "Assign to Categories (Optional)",
                options=list(category_map.keys())
            )

            submitted = st.form_submit_button("Create Document")

            if submitted:
                if filename and content:
                    selected_category_ids = [category_map[name] for name in selected_categories]
                    with st.spinner("Creating and processing your document..."):
                        create_from_text(
                            st.session_state.token,
                            filename,
                            content,
                            selected_category_ids
                        )
                    st.success(f"Document '{filename}' created successfully!")
                else:
                    st.error("Please provide both a filename and content.")

    except requests.exceptions.RequestException as e:
        st.error(f"An API error occurred: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
