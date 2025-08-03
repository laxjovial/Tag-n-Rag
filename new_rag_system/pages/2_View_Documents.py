import streamlit as st
import pandas as pd
import requests
from app.utils import check_auth

# --- Authentication Check ---
check_auth("View Documents")

# --- Page Configuration ---
st.set_page_config(page_title="View Documents", layout="wide")

# --- API Configuration ---
API_BASE_URL = "http://127.0.0.1:8000"

# --- Helper Functions ---
def get_auth_headers():
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"}

@st.cache_data(ttl=60)
def get_user_documents(search_query=""):
    """Fetches documents for the current user, with an optional search query."""
    params = {"search": search_query} if search_query else {}
    response = requests.get(f"{API_BASE_URL}/documents/", headers=get_auth_headers(), params=params)
    response.raise_for_status()
    return response.json()

def delete_document(doc_id: int):
    """Deletes a document by its ID."""
    response = requests.delete(f"{API_BASE_URL}/documents/{doc_id}", headers=get_auth_headers())
    response.raise_for_status()
    return True

# --- UI Rendering ---
st.title("View and Manage Your Documents")

# Search bar
search_term = st.text_input("Search by filename", key="doc_search")

try:
    with st.spinner("Loading your documents..."):
        documents_data = get_user_documents(search_term)

    if not documents_data:
        st.info("You haven't uploaded any documents yet, or no documents match your search.")
    else:
        df = pd.DataFrame(documents_data)
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        df['expires_at'] = pd.to_datetime(df['expires_at']).dt.strftime('%Y-%m-%d %H:%M') if 'expires_at' in df else "N/A"

        # Add action columns
        df['Edit'] = [f"[Edit](7_Edit_Document?doc_id={id})" for id in df['id']]

        # Display documents in a more user-friendly way
        for index, row in df.iterrows():
            with st.container(border=True):
                col1, col2, col3 = st.columns([4, 1, 1])
                with col1:
                    st.subheader(row['original_filename'])
                    st.caption(f"Version: {row['version']} | Created: {row['created_at']}")
                with col2:
                    st.page_link("pages/7_Edit_Document.py", label="Edit", icon="✏️",
                                 query_params={"doc_id": row['id']})
                with col3:
                    if st.button("Delete", key=f"delete_{row['id']}", type="primary"):
                        try:
                            delete_document(row['id'])
                            st.success(f"Document '{row['original_filename']}' deleted.")
                            st.rerun()
                        except requests.exceptions.RequestException as e:
                            st.error(f"Failed to delete document: {e}")

except requests.exceptions.RequestException as e:
    st.error(f"Failed to load documents: {e}")
except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
