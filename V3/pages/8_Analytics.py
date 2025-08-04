import streamlit as st
import pandas as pd
import requests
from src.frontend.utils import check_auth

# --- Authentication Check ---
check_auth("My Analytics")

# --- Page Configuration ---
st.set_page_config(page_title="My Analytics", layout="wide")

# --- API Configuration ---
API_BASE_URL = "http://127.0.0.1:8000"

# --- Helper Functions ---
def get_auth_headers():
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"}

@st.cache_data(ttl=60)
def get_my_analytics():
    response = requests.get(f"{API_BASE_URL}/history/analytics", headers=get_auth_headers())
    response.raise_for_status()
    return response.json()

@st.cache_data(ttl=60)
def get_user_profile():
    response = requests.get(f"{API_BASE_URL}/user/me", headers=get_auth_headers())
    response.raise_for_status()
    return response.json()

def format_bytes(size_bytes):
    """Converts bytes to a human-readable format."""
    if size_bytes == 0:
        return "0 B"
    power = 1024
    n = 0
    power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size_bytes > power and n < len(power_labels) -1 :
        size_bytes /= power
        n += 1
    return f"{size_bytes:.2f} {power_labels[n]}B"

# --- UI Rendering ---
st.title("My Personal Analytics")

try:
    with st.spinner("Loading your analytics..."):
        analytics_data = get_my_analytics()
        user_profile = get_user_profile()

    st.header("Storage Usage")
    storage_used = user_profile.get("storage_used", 0)
    storage_limit = user_profile.get("storage_limit", 1) # Avoid division by zero

    if storage_limit > 0:
        percent_used = min(storage_used / storage_limit, 1.0)
        st.progress(percent_used)
        st.metric(
            label="Your Storage",
            value=f"{format_bytes(storage_used)} of {format_bytes(storage_limit)}",
            help="This is the total size of all documents you have uploaded."
        )
    else:
        st.metric("Storage Used", format_bytes(storage_used))

    st.divider()

    st.header("Query Usage")
    if not analytics_data or analytics_data["total_queries"] == 0:
        st.info("You don't have any query usage data to analyze yet.")
    else:
        col1, col2 = st.columns(2)
        col1.metric(label="Total Queries Made", value=analytics_data.get("total_queries", 0))
        col2.metric(label="Most Queried Documents", value=len(analytics_data.get("top_documents", [])))

        queries_per_day = analytics_data.get("queries_per_day")
        if queries_per_day:
            st.subheader("Your Query Activity")
            df_queries = pd.DataFrame(queries_per_day)
            df_queries['date'] = pd.to_datetime(df_queries['date'])
            st.bar_chart(df_queries.set_index('date')['queries'], use_container_width=True)

        top_docs = analytics_data.get("top_documents")
        if top_docs:
            st.subheader("Your Most Frequently Queried Documents")
            df_docs = pd.DataFrame(top_docs)
            st.dataframe(df_docs, use_container_width=True)

except requests.exceptions.RequestException as e:
    st.error(f"Failed to load your analytics: {e}")
except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
