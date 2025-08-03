import streamlit as st
import requests
from typing import List, Dict, Optional
from app.utils import check_auth

# --- Authentication Check ---
check_auth("Query Documents")

st.set_page_config(page_title="Query Documents", layout="wide")

API_BASE_URL = "http://127.0.0.1:8000"

# --- API Functions ---
def get_auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

@st.cache_data(ttl=60)
def get_user_data() -> Dict:
    headers = get_auth_headers()
    docs_response = requests.get(f"{API_BASE_URL}/documents/", headers=headers)
    docs_response.raise_for_status()
    cats_response = requests.get(f"{API_BASE_URL}/categories/", headers=headers)
    cats_response.raise_for_status()
    llm_configs_response = requests.get(f"{API_BASE_URL}/admin/llm_configs/", headers=headers)
    llm_configs_response.raise_for_status()
    return {
        "documents": docs_response.json(),
        "categories": cats_response.json(),
        "llm_configs": llm_configs_response.json()
    }

def run_query(question: str, doc_ids: Optional[List[int]] = None, cat_id: Optional[int] = None, llm_config_id: Optional[int] = None) -> Dict:
    headers = get_auth_headers()
    payload = {"question": question}
    if cat_id is not None:
        payload["category_id"] = cat_id
    elif doc_ids:
        payload["document_ids"] = doc_ids
    else:
        raise ValueError("Either doc_ids or cat_id must be provided.")
    if llm_config_id is not None:
        payload["llm_config_id"] = llm_config_id
    response = requests.post(f"{API_BASE_URL}/query/", json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

def save_query_as_document(query_id: int, filename: str):
    headers = get_auth_headers()
    data = {"new_filename": filename}
    response = requests.post(f"{API_BASE_URL}/query/{query_id}/save_as_document", data=data, headers=headers)
    response.raise_for_status()
    return response.json()

# --- Main App ---
st.title("Query Your Documents")

try:
    with st.spinner("Loading your data..."):
        user_data = get_user_data()
        documents = user_data["documents"]
        categories = user_data["categories"]
        llm_configs = user_data["llm_configs"]
        doc_map = {doc['original_filename']: doc['id'] for doc in documents}
        cat_map = {cat['name']: cat['id'] for cat in categories}
        llm_config_map = {config['name']: config['id'] for config in llm_configs}

    with st.sidebar:
        st.header("1. Select what to query")
        query_target = st.radio("Query a category or specific documents?", ("Category", "Specific Documents"), horizontal=True)
        selected_doc_ids = None
        selected_cat_id = None
        if query_target == "Category":
            if categories:
                cat_name = st.selectbox("Choose a category", list(cat_map.keys()))
                selected_cat_id = cat_map.get(cat_name)
            else:
                st.info("No categories available.")
        else:
            if documents:
                selected_doc_names = st.multiselect("Choose documents", list(doc_map.keys()))
                selected_doc_ids = [doc_map[name] for name in selected_doc_names]
            else:
                st.info("No documents available.")
        st.header("2. Configure Model (Optional)")
        selected_llm_config_id = None
        if llm_configs:
            llm_config_name = st.selectbox("Model", list(llm_config_map.keys()))
            selected_llm_config_id = llm_config_map.get(llm_config_name)
        st.slider("Creativity Control", 0.0, 1.0, 0.7)

    question = st.text_area("3. Ask your question", height=150)

    if st.button("Get Answer"):
        is_valid_selection = (query_target == "Category" and selected_cat_id is not None) or \
                             (query_target == "Specific Documents" and selected_doc_ids)
        if not question:
            st.warning("Please enter a question.")
        elif not is_valid_selection:
            st.warning("Please select at least one document or a category.")
        else:
            with st.spinner("Finding answers..."):
                result = run_query(question, selected_doc_ids, selected_cat_id, selected_llm_config_id)
                st.session_state.last_answer = result.get("answer")
                st.session_state.last_query_id = result.get("query_id")

    if st.session_state.get("last_answer"):
        st.markdown("---")
        st.subheader("Answer")
        st.markdown(st.session_state.last_answer)

        with st.expander("Save this result as a new document"):
            with st.form("save_as_doc_form"):
                new_filename = st.text_input("Enter a filename for the new document")
                submitted = st.form_submit_button("Save")
                if submitted:
                    if not new_filename:
                        st.error("Filename cannot be empty.")
                    else:
                        try:
                            with st.spinner("Saving document..."):
                                save_query_as_document(st.session_state.last_query_id, new_filename)
                                st.success(f"Result saved as '{new_filename}'!")
                                # Clear cache for document list to refresh it on other pages
                                st.cache_data.clear()
                        except requests.exceptions.RequestException as e:
                            st.error(f"Failed to save document: {e}")

except requests.exceptions.RequestException as e:
    st.error(f"An API error occurred: {e}")
except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
