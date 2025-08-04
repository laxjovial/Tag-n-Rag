import streamlit as st
import requests
from typing import List, Dict, Optional
from src.frontend.utils import check_auth

# --- Authentication Check ---
check_auth("Query Documents")

st.set_page_config(page_title="Query Documents", layout="wide")

API_BASE_URL = "http://127.0.0.1:8000"

# --- API Functions ---
def get_auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

@st.cache_data(ttl=60)
def get_user_data() -> Dict:
    # ... (same as before)
    pass

def run_query(question: str, doc_ids: Optional[List[int]] = None, cat_id: Optional[int] = None, llm_config_id: Optional[int] = None, conversation_id: Optional[str] = None) -> Dict:
    headers = get_auth_headers()
    payload = {
        "question": question,
        "document_ids": doc_ids,
        "category_id": cat_id,
        "llm_config_id": llm_config_id,
        "conversation_id": conversation_id
    }
    response = requests.post(f"{API_BASE_URL}/query/", json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

# --- Main App ---
st.title("Query Your Documents")

# Initialize chat history and conversation_id in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

try:
    # ... (Data loading logic is the same)

    # --- Sidebar for document selection ---
    # ... (Sidebar logic is the same)

    # --- Main Chat Interface ---
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a follow-up question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with st.spinner("Thinking..."):
                # This is a simplified version. The doc/category selection would
                # need to be handled within the chat flow.
                # For now, we assume the context is carried by the conversation_id.
                response = run_query(
                    question=prompt,
                    conversation_id=st.session_state.conversation_id
                    # In a real app, you'd re-use the selected docs/category
                    # or allow changing them.
                )
                message_placeholder.markdown(response["answer"])
                st.session_state.conversation_id = response["conversation_id"]

            st.session_state.messages.append({"role": "assistant", "content": response["answer"]})

except Exception as e:
    st.error(f"An error occurred: {e}")
