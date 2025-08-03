import streamlit as st
import requests
from app.utils import check_auth

# --- Authentication Check ---
check_auth("Edit Document")

# --- Page Configuration ---
st.set_page_config(page_title="Edit Document", layout="wide")

# --- API Configuration ---
API_BASE_URL = "http://127.0.0.1:8000"

# --- Helper Functions ---
def get_auth_headers():
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"}

@st.cache_data(ttl=10) # Short cache to allow quick refresh after save
def get_document_content(doc_id):
    """Fetches the text content of a specific document."""
    response = requests.get(f"{API_BASE_URL}/documents/{doc_id}/content", headers=get_auth_headers())
    response.raise_for_status()
    return response.text

def update_document_content(doc_id, new_content):
    """Updates the content of a specific document."""
    payload = {"content": new_content}
    response = requests.put(f"{API_BASE_URL}/documents/{doc_id}", json=payload, headers=get_auth_headers())
    response.raise_for_status()
    return response.json()

# --- UI Rendering ---
st.title("Edit Document")

# Get doc_id from query parameters
doc_id_to_edit = st.query_params.get("doc_id")

if not doc_id_to_edit:
    st.error("No document selected for editing.")
    st.info("Please select a document from the 'View Documents' page.")
    st.page_link("pages/2_View_Documents.py", label="Go to View Documents", icon="📄")
else:
    try:
        doc_id_to_edit = int(doc_id_to_edit) # Ensure it's an integer
        with st.spinner("Loading document content..."):
            content = get_document_content(doc_id_to_edit)

        with st.form("edit_document_form"):
            edited_content = st.text_area(
                "Document Content",
                value=content,
                height=600,
                help="Edit the content of your document here."
            )
            submitted = st.form_submit_button("Save Changes")

            if submitted:
                with st.spinner("Saving your changes..."):
                    update_document_content(doc_id_to_edit, edited_content)
                    # Invalidate cache for this function to get fresh content
                    st.cache_data.clear()
                    st.success("Document updated successfully!")
                    st.page_link("pages/2_View_Documents.py", label="Return to Documents", icon="✅")

    except (ValueError, TypeError):
        st.error("Invalid document ID in the URL.")
    except requests.exceptions.RequestException as e:
        if e.response and e.response.status_code == 404:
            st.error("Document not found. It may have been deleted or you may not have permission to view it.")
        else:
            st.error(f"Failed to load or update document: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
