import streamlit as st
import requests

st.set_page_config(page_title="Edit Document", layout="wide")

API_BASE_URL = "http://localhost:8000"

def get_document_content(doc_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE_URL}/documents/{doc_id}/content", headers=headers)
    response.raise_for_status()
    return response.text

def update_document_content(doc_id, content, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(
        f"{API_BASE_URL}/documents/{doc_id}",
        json={"content": content},
        headers=headers
    )
    response.raise_for_status()
    return response.json()

st.title("Edit Document")

if 'token' not in st.session_state or st.session_state.token is None:
    st.warning("Please log in to edit documents.")
else:
    doc_id_to_edit = st.query_params.get("doc_id")
    if not doc_id_to_edit:
        st.error("No document selected for editing. Please select a document from the 'View Documents' page.")
    else:
        try:
            if "doc_content" not in st.session_state or st.session_state.get("editing_doc_id") != doc_id_to_edit:
                with st.spinner("Loading document..."):
                    st.session_state.doc_content = get_document_content(doc_id_to_edit, st.session_state.token)
                    st.session_state.editing_doc_id = doc_id_to_edit

            content = st.text_area("Document Content", value=st.session_state.doc_content, height=600)

            if st.button("Save Changes"):
                with st.spinner("Saving..."):
                    update_document_content(doc_id_to_edit, content, st.session_state.token)
                    st.success("Document updated successfully!")
                    # Clear the cached content to force a reload on next view
                    del st.session_state.doc_content
                    del st.session_state.editing_doc_id

        except requests.exceptions.RequestException as e:
            st.error(f"Failed to load or update document: {e}")
