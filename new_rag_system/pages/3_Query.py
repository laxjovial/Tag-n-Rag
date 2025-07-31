import streamlit as st
import requests
from typing import List, Dict

st.set_page_config(page_title="Query Documents", layout="wide")

API_BASE_URL = "http://localhost:8000"

# --- API Functions ---
def get_user_data(token: str) -> Dict:
    headers = {"Authorization": f"Bearer {token}"}
    docs_response = requests.get(f"{API_BASE_URL}/documents/", headers=headers)
    docs_response.raise_for_status()

    cats_response = requests.get(f"{API_BASE_URL}/categories/", headers=headers)
    cats_response.raise_for_status()

    # In a real app, you'd fetch LLM configs from an admin endpoint
    # For now, we'll hardcode them.
    llm_configs = [{"name": "Default GPT-3.5"}]

    return {
        "documents": docs_response.json(),
        "categories": cats_response.json(),
        "llm_configs": llm_configs
    }

def run_query(token: str, question: str, doc_ids: List[int] = None, cat_id: int = None) -> Dict:
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"question": question}
    if cat_id:
        payload["category_id"] = cat_id
    elif doc_ids:
        payload["document_ids"] = doc_ids
    else:
        raise ValueError("Either doc_ids or cat_id must be provided.")

    response = requests.post(f"{API_BASE_URL}/query/", json=payload, headers=headers)
    response.raise_for_status()
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
                cat_name = st.selectbox("Choose a category", list(cat_map.keys()))
                selected_cat_id = cat_map.get(cat_name)
            else:
                doc_names = st.multiselect("Choose documents", list(doc_map.keys()))
                selected_doc_ids = [doc_map[name] for name in doc_names]

            st.header("2. Configure Model (Optional)")
            st.selectbox("Model", [config['name'] for config in llm_configs])
            st.slider("Temperature", 0.0, 1.0, 0.7)

        question = st.text_area("3. Ask your question", height=150)

        if st.button("Get Answer"):
            if not question:
                st.warning("Please enter a question.")
            elif not selected_doc_ids and not selected_cat_id:
                st.warning("Please select at least one document or a category to query.")
            else:
                with st.spinner("Finding answers..."):
                    result = run_query(
                        st.session_state.token,
                        question,
                        doc_ids=selected_doc_ids,
                        cat_id=selected_cat_id
                    )
                    st.session_state.last_answer = result.get("answer")
                    st.session_state.last_query_id = result.get("query_id") # Assuming the API returns this

        # --- Display Answer ---
        if "last_answer" in st.session_state and st.session_state.last_answer:
            st.markdown("---")
            st.subheader("Answer")
            st.write(st.session_state.last_answer)
            # The export buttons will be on the dedicated Export page

    except requests.exceptions.RequestException as e:
        st.error(f"An API error occurred: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
