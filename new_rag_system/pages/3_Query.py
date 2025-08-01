import streamlit as st
import requests
from typing import List, Dict, Optional

st.set_page_config(page_title="Query Documents", layout="wide")

API_BASE_URL = "http://127.0.0.1:8000"

# --- API Functions ---
def get_user_data(token: str) -> Dict:
    """
    Fetches user's documents, categories, and LLM configurations from the backend.
    """
    headers = {"Authorization": f"Bearer {token}"}

    docs_response = requests.get(f"{API_BASE_URL}/documents/", headers=headers)
    docs_response.raise_for_status()

    cats_response = requests.get(f"{API_BASE_URL}/categories/", headers=headers)
    cats_response.raise_for_status()

    # Fetch LLM configurations from the backend
    llm_configs_response = requests.get(f"{API_BASE_URL}/admin/llm_configs/", headers=headers)
    llm_configs_response.raise_for_status()

    return {
        "documents": docs_response.json(),
        "categories": cats_response.json(),
        "llm_configs": llm_configs_response.json()
    }

def run_query(token: str, question: str, doc_ids: Optional[List[int]] = None, cat_id: Optional[int] = None, llm_config_id: Optional[int] = None) -> Dict:
    """
    Sends a query request to the backend API.
    """
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"question": question}

    if cat_id is not None: # Use 'is not None' to differentiate from 0
        payload["category_id"] = cat_id
    elif doc_ids is not None and len(doc_ids) > 0: # Check if list is not empty
        payload["document_ids"] = doc_ids
    else:
        # This case should be caught by frontend validation, but good to have a fallback
        raise ValueError("Either doc_ids or cat_id must be provided.")

    if llm_config_id is not None:
        payload["llm_config_id"] = llm_config_id

    response = requests.post(f"{API_BASE_URL}/query/", json=payload, headers=headers)
    response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
    return response.json()


st.title("Query Your Documents")

if 'token' not in st.session_state or st.session_state.token is None:
    st.warning("Please log in to query documents.")
else:
    try:
        with st.spinner("Loading your data..."):
            user_data = get_user_data(st.session_state.token)
            documents = user_data["documents"]
            categories = user_data["categories"]
            llm_configs = user_data["llm_configs"]

            doc_map = {doc['original_filename']: doc['id'] for doc in documents}
            cat_map = {cat['name']: cat['id'] for cat in categories}
            llm_config_map = {config['name']: config['id'] for config in llm_configs}


        # --- Query Interface ---
        with st.sidebar:
            st.header("1. Select what to query")
            query_target = st.radio(
                "Query a category or specific documents?",
                ("Category", "Specific Documents"),
                horizontal=True
            )

            selected_doc_ids = None
            selected_cat_id = None

            if query_target == "Category":
                # Ensure categories exist before showing selectbox
                if categories:
                    cat_names = list(cat_map.keys())
                    cat_name = st.selectbox("Choose a category", cat_names)
                    selected_cat_id = cat_map.get(cat_name)
                else:
                    st.info("No categories available. Create some in the dashboard or upload page.")
            else:
                # Ensure documents exist before showing multiselect
                if documents:
                    doc_names = list(doc_map.keys())
                    selected_doc_names = st.multiselect("Choose documents", doc_names)
                    selected_doc_ids = [doc_map[name] for name in selected_doc_names]
                else:
                    st.info("No documents available. Upload some first!")

            st.header("2. Configure Model (Optional)")
            selected_llm_config_id = None
            if llm_configs:
                llm_config_names = [config['name'] for config in llm_configs]
                selected_llm_config_name = st.selectbox("Model", llm_config_names)
                selected_llm_config_id = llm_config_map.get(selected_llm_config_name)
            else:
                st.info("No LLM configurations found. Please add one via the Admin panel.")

            st.slider("Temperature", 0.0, 1.0, 0.7, help="Controls the randomness of the model's output.")

        question = st.text_area("3. Ask your question", height=150)

        if st.button("Get Answer"):
            if not question:
                st.warning("Please enter a question.")
            elif (query_target == "Category" and selected_cat_id is None) or \
                 (query_target == "Specific Documents" and (selected_doc_ids is None or len(selected_doc_ids) == 0)):
                st.warning("Please select at least one document or a category to query.")
            else:
                with st.spinner("Finding answers..."):
                    result = run_query(
                        st.session_state.token,
                        question,
                        doc_ids=selected_doc_ids,
                        cat_id=selected_cat_id,
                        llm_config_id=selected_llm_config_id # Pass the selected LLM config ID
                    )
                    st.session_state.last_answer = result.get("answer")
                    st.session_state.last_query_id = result.get("query_id")

        # --- Display Answer ---
        if "last_answer" in st.session_state and st.session_state.last_answer:
            st.markdown("---")
            st.subheader("Answer")
            st.write(st.session_state.last_answer)
            # You might want to add a button here to navigate to the Export page
            # and pass st.session_state.last_query_id
            # Example (requires Streamlit 1.33+ for query_params or use session_state):
            # if st.button("Export Answer"):
            #     st.session_state['export_query_id'] = st.session_state.last_query_id
            #     st.switch_page("pages/9_Export.py")


    except requests.exceptions.RequestException as e:
        st.error(f"An API error occurred: {e}")
        if e.response is not None:
            try:
                error_detail = e.response.json().get('detail', 'No additional detail provided.')
                st.error(f"Server response detail: {error_detail}")
            except requests.exceptions.JSONDecodeError:
                st.error(f"Server returned non-JSON response: {e.response.text}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

