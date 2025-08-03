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






    response = requests.delete(f"{API_BASE_URL}/documents/{doc_id}", headers=get_auth_headers())
    response.raise_for_status()
    st.cache_data.clear() # Clear cache after deleting
    return True

@st.cache_data(ttl=15) # Cache export content briefly
def export_document(doc_id: int, file_format: str):
    """Exports a document in the specified format."""
    params = {"format": file_format}
    response = requests.get(f"{API_BASE_URL}/documents/{doc_id}/export", headers=get_auth_headers(), params=params)
    response.raise_for_status()
    return response.content

# --- UI Rendering ---

st.title("View and Manage Your Documents")

search_term = st.text_input("Search by filename", key="doc_search")

try:
    with st.spinner("Loading your documents..."):
        documents_data = get_user_documents(search_term)

    if not documents_data:
        st.info("You haven't uploaded any documents yet, or no documents match your search.")
    else:
        for doc in documents_data:
            with st.container(border=True):
                col1, col2, col3 = st.columns([4, 1, 1])
                with col1:
                    st.subheader(doc['original_filename'])
                    st.caption(f"Version: {doc['version']} | Created: {pd.to_datetime(doc['created_at']).strftime('%Y-%m-%d %H:%M')}")
                with col2:
                    st.page_link("pages/7_Edit_Document.py", label="Edit", icon="✏️", query_params={"doc_id": doc['id']})
                with col3:
                    if st.button("Delete", key=f"delete_{doc['id']}", type="primary"):
                        try:
                            delete_document(doc['id'])
                            st.success(f"Document '{doc['original_filename']}' deleted.")
                            st.rerun()
                        except requests.exceptions.RequestException as e:
                            st.error(f"Failed to delete document: {e}")

                # Export buttons
                with st.expander("Export Document"):
                    b_col1, b_col2, b_col3 = st.columns(3)
                    with b_col1:
                        st.download_button(
                            label="as PDF",
                            data=export_document(doc['id'], "pdf"),
                            file_name=f"{doc['original_filename']}.pdf",
                            mime="application/pdf",
                            key=f"pdf_{doc['id']}"
                        )
                    with b_col2:
                        st.download_button(
                            label="as DOCX",
                            data=export_document(doc['id'], "docx"),
                            file_name=f"{doc['original_filename']}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key=f"docx_{doc['id']}"
                        )
                    with b_col3:
                        st.download_button(
                            label="as TXT",
                            data=export_document(doc['id'], "txt"),
                            file_name=f"{doc['original_filename']}.txt",
                            mime="text/plain",
                            key=f"txt_{doc['id']}"
                        )

st.title("View and Manage Your Documents")

search_term = st.text_input("Search by filename", key="doc_search")


try:
    with st.spinner("Loading your documents..."):
        documents_data = get_user_documents(search_term)

    if not documents_data:
        st.info("You haven't uploaded any documents yet, or no documents match your search.")
    else:
        for doc in documents_data:
            with st.container(border=True):
                col1, col2, col3 = st.columns([4, 1, 1])
                with col1:
                    st.subheader(doc['original_filename'])
                    st.caption(f"Version: {doc['version']} | Created: {pd.to_datetime(doc['created_at']).strftime('%Y-%m-%d %H:%M')}")
                with col2:
                    st.page_link("pages/7_Edit_Document.py", label="Edit", icon="✏️", query_params={"doc_id": doc['id']})
                with col3:
                    if st.button("Delete", key=f"delete_{doc['id']}", type="primary"):
                        try:
                            delete_document(doc['id'])
                            st.success(f"Document '{doc['original_filename']}' deleted.")


try:
    with st.spinner("Loading your documents..."):
        documents_data = get_user_documents(search_term)

    if not documents_data:
        st.info("You haven't uploaded any documents yet, or no documents match your search.")
    else:
        for doc in documents_data:
            with st.container(border=True):
                col1, col2, col3 = st.columns([4, 1, 1])
                with col1:
                    st.subheader(doc['original_filename'])
                    st.caption(f"Version: {doc['version']} | Created: {pd.to_datetime(doc['created_at']).strftime('%Y-%m-%d %H:%M')}")
                with col2:
                    st.page_link("pages/7_Edit_Document.py", label="Edit", icon="✏️", query_params={"doc_id": doc['id']})
                with col3:
                    if st.button("Delete", key=f"delete_{doc['id']}", type="primary"):
                        try:
                            delete_document(doc['id'])
                            st.success(f"Document '{doc['original_filename']}' deleted.")
                            st.rerun()
                        except requests.exceptions.RequestException as e:
                            st.error(f"Failed to delete document: {e}")

                # Export buttons
                with st.expander("Export Document"):
                    b_col1, b_col2, b_col3 = st.columns(3)
                    with b_col1:
                        st.download_button(
                            label="as PDF",
                            data=export_document(doc['id'], "pdf"),
                            file_name=f"{doc['original_filename']}.pdf",
                            mime="application/pdf",
                            key=f"pdf_{doc['id']}"
                        )
                    with b_col2:
                        st.download_button(
                            label="as DOCX",
                            data=export_document(doc['id'], "docx"),
                            file_name=f"{doc['original_filename']}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key=f"docx_{doc['id']}"
                        )
                    with b_col3:
                        st.download_button(
                            label="as TXT",
                            data=export_document(doc['id'], "txt"),
                            file_name=f"{doc['original_filename']}.txt",
                            mime="text/plain",
                            key=f"txt_{doc['id']}"
                        )
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


                # Export buttons
                with st.expander("Export Document"):
                    b_col1, b_col2, b_col3 = st.columns(3)
                    with b_col1:
                        st.download_button(
                            label="as PDF",
                            data=export_document(doc['id'], "pdf"),
                            file_name=f"{doc['original_filename']}.pdf",
                            mime="application/pdf",
                            key=f"pdf_{doc['id']}"
                        )
                    with b_col2:
                        st.download_button(
                            label="as DOCX",
                            data=export_document(doc['id'], "docx"),
                            file_name=f"{doc['original_filename']}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key=f"docx_{doc['id']}"
                        )
                    with b_col3:
                        st.download_button(
                            label="as TXT",
                            data=export_document(doc['id'], "txt"),
                            file_name=f"{doc['original_filename']}.txt",
                            mime="text/plain",
                            key=f"txt_{doc['id']}"
                        )




except requests.exceptions.RequestException as e:
    st.error(f"Failed to load documents: {e}")
except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
