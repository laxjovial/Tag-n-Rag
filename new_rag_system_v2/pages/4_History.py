import streamlit as st
import pandas as pd
import requests
from app.utils import check_auth

# --- Authentication Check ---
check_auth("Query History")

# --- Page Configuration ---
st.set_page_config(page_title="Query History", layout="wide")

# --- API Configuration ---
API_BASE_URL = "http://127.0.0.1:8000"

# --- Helper Functions ---
def get_auth_headers():
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"}

@st.cache_data(ttl=60)
def get_history():
    """Fetches query history for the current user."""
    response = requests.get(f"{API_BASE_URL}/history/", headers=get_auth_headers())
    response.raise_for_status()
    return response.json()

# --- UI Rendering ---
st.title("Your Query History")

try:
    with st.spinner("Loading your history..."):
        history_data = get_history()

    if not history_data:
        st.info("You do not have any query history yet.")
    else:
        df = pd.DataFrame(history_data)
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')

        # Display history in a more readable format
        for index, row in df.iterrows():
            with st.container(border=True):
                st.caption(f"On {row['created_at']}")
                st.markdown(f"**Q:** {row['question']}")
                if 'response' in row and row['response']:
                    st.markdown(f"**A:** {row['response']}")
                st.caption(f"Document ID: {row.get('document_id', 'N/A')} | Relevant: {row.get('is_relevant', 'N/A')}")

except requests.exceptions.RequestException as e:
    st.error(f"Failed to load history: {e}")
except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
