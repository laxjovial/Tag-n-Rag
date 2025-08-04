import streamlit as st
import requests
from typing import List, Dict, Optional

from src.frontend.utils import check_auth

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

    # Fetch all data in parallel could be an option here


    # Fetch all data in parallel could be an option here


    docs_response = requests.get(f"{API_BASE_URL}/documents/", headers=headers)
    docs_response.raise_for_status()
    cats_response = requests.get(f"{API_BASE_URL}/categories/", headers=headers)
    cats_response.raise_for_status()
    llm_configs_response = requests.get(f"{API_BASE_URL}/admin/llm_configs/", headers=headers)
    llm_configs_response.raise_for_status()


    mappings_response = requests.get(f"{API_BASE_URL}/mappings/", headers=headers)
    mappings_response.raise_for_status()
    return {
        "documents": docs_response.json(),
        "categories": cats_response.json(),
        "llm_configs": llm_configs_response.json(),
        "mappings": mappings_response.json()
    }

def run_query(question: str, doc_ids: Optional[List[int]] = None, cat_id: Optional[int] = None, llm_config_id: Optional[int] = None) -> Dict:
    # ... (same as before)


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

    # ... (same as before)


    # ... (same as before)


    headers = get_auth_headers()
    data = {"new_filename": filename}
    response = requests.post(f"{API_BASE_URL}/query/{query_id}/save_as_document", data=data, headers=headers)
    response.raise_for_status()
    return response.json()

def append_to_document(doc_id: int, query_id: int, formatting_method: str):

    # ... (same as before)


    # ... (same as before)


    headers = get_auth_headers()
    payload = {"query_id": query_id, "formatting_method": formatting_method}
    response = requests.post(f"{API_BASE_URL}/documents/{doc_id}/append", json=payload, headers=headers)
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



        mappings = user_data["mappings"]

        doc_map = {doc['original_filename']: doc['id'] for doc in documents}
        cat_map = {cat['name']: cat['id'] for cat in categories}
        llm_config_map = {config['name']: config['id'] for config in llm_configs}
        mapped_cat_ids = {m['category_id'] for m in mappings}


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



                # Add icon to mapped categories
                cat_display_names = [f"{cat['name']} ☁️" if cat['id'] in mapped_cat_ids else cat['name'] for cat in categories]
                selected_display_name = st.selectbox("Choose a category", cat_display_names)
                # Find original name to get ID
                original_name = selected_display_name.replace(" ☁️", "")
                selected_cat_id = cat_map.get(original_name)


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
        # ... (rest of the sidebar is the same)


        st.header("2. Configure Model (Optional)")
        # ... (rest of the sidebar is the same)

        st.header("2. Configure Model (Optional)")


        selected_llm_config_id = None
        if llm_configs:
            llm_config_name = st.selectbox("Model", list(llm_config_map.keys()))
            selected_llm_config_id = llm_config_map.get(llm_config_name)
        st.slider("Creativity Control", 0.0, 1.0, 0.7)

    question = st.text_area("3. Ask your question", height=150)

    if st.button("Get Answer"):

        # ... (same as before)


        # ... (same as before)


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
        # ... (same as before)




        st.markdown("---")
        st.subheader("Answer")
        st.markdown(st.session_state.last_answer)

        with st.expander("Save or Append this Result"):
            tab1, tab2 = st.tabs(["Save as New Document", "Append to Existing Document"])
            with tab1:
                with st.form("save_as_doc_form"):
                    new_filename = st.text_input("Enter a filename for the new document")
                    submitted = st.form_submit_button("Save as New")
                    if submitted:
                        if not new_filename:
                            st.error("Filename cannot be empty.")
                        else:
                            try:
                                with st.spinner("Saving document..."):
                                    save_query_as_document(st.session_state.last_query_id, new_filename)
                                    st.success(f"Result saved as '{new_filename}'!")
                                    st.cache_data.clear()
                            except requests.exceptions.RequestException as e:
                                st.error(f"Failed to save document: {e}")
            with tab2:
                if not documents:
                    st.info("You have no documents to append to.")
                else:
                    with st.form("append_to_doc_form"):
                        doc_to_append_name = st.selectbox("Select document to append to", list(doc_map.keys()))
                        formatting_method = st.radio(
                            "Choose append format",
                            [('simple', 'Simple Separator (---)'),
                             ('informative', 'Informative Timestamp'),
                             ('structured', 'Structured Block')],
                            format_func=lambda x: x[1]
                        )
                        append_submitted = st.form_submit_button("Append to Document")
                        if append_submitted:
                            doc_id = doc_map.get(doc_to_append_name)
                            try:
                                with st.spinner("Appending to document..."):
                                    append_to_document(doc_id, st.session_state.last_query_id, formatting_method[0])
                                    st.success(f"Successfully appended to '{doc_to_append_name}'!")
                                    st.cache_data.clear()
                            except requests.exceptions.RequestException as e:
                                st.error(f"Failed to append to document: {e}")

except requests.exceptions.RequestException as e:
    st.error(f"An API error occurred: {e}")
except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
