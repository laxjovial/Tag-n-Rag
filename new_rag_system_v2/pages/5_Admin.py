import streamlit as st
import pandas as pd
import requests
from src.frontend.utils import check_admin_auth

# --- Authentication Check ---
check_admin_auth()

# --- Page Configuration ---
st.set_page_config(page_title="Admin Dashboard", layout="wide")

# --- API Configuration ---
API_BASE_URL = "http://127.0.0.1:8000"

# --- Helper Functions ---
def get_auth_headers():
    """Returns the authorization headers for API requests."""
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"}

@st.cache_data(ttl=60)
def get_all_users():
    """Fetches all users from the API."""
    response = requests.get(f"{API_BASE_URL}/admin/users/", headers=get_auth_headers())
    response.raise_for_status()
    return response.json()

@st.cache_data(ttl=60)
def get_llm_configs():
    """Fetches all LLM configs from the API."""
    response = requests.get(f"{API_BASE_URL}/admin/llm_configs/", headers=get_auth_headers())
    response.raise_for_status()
    return response.json()

@st.cache_data(ttl=300)
def get_global_history():
    """Fetches global query history from the API."""
    response = requests.get(f"{API_BASE_URL}/admin/history/", headers=get_auth_headers())
    response.raise_for_status()
    return response.json()

@st.cache_data(ttl=300)
def get_system_analytics():
    """Fetches system analytics from the API."""
    response = requests.get(f"{API_BASE_URL}/admin/analytics/queries_per_day/", headers=get_auth_headers())
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
st.title("Admin Dashboard")

tab1, tab2, tab3, tab4 = st.tabs([
    "User Management",
    "LLM/API Configs",
    "Global History",
    "System Analytics"
])

# --- User Management Tab ---
with tab1:
    st.header("Manage Users")
    try:
        with st.spinner("Loading users..."):
            users_data = get_all_users()

        if users_data:
            df = pd.DataFrame(users_data)
            # Format storage usage for display
            df['storage_used_hr'] = df['storage_used'].apply(format_bytes)
            df['storage_limit_hr'] = df['storage_limit'].apply(format_bytes)

            df_display = df[["id", "username", "role", "storage_used_hr", "storage_limit_hr"]]
            df_display = df_display.rename(columns={
                "storage_used_hr": "Storage Used",
                "storage_limit_hr": "Storage Limit"
            })
            st.dataframe(df_display, use_container_width=True)
        else:
            st.info("No users found.")

    except requests.exceptions.RequestException as e:
        st.error(f"Failed to load users: {e}")

# --- LLM/API Configs Tab ---
with tab2:
    st.header("Manage LLM and API Configurations")
    try:
        with st.spinner("Loading configurations..."):
            configs_data = get_llm_configs()

        if configs_data:
            df = pd.DataFrame(configs_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No configurations found.")

    except requests.exceptions.RequestException as e:
        st.error(f"Failed to load configurations: {e}")

# --- Global History Tab ---
with tab3:
    st.header("Global Query History")
    try:
        with st.spinner("Loading history..."):
            history_data = get_global_history()

        if history_data:
            df = pd.DataFrame(history_data)
            df['created_at'] = pd.to_datetime(df['created_at'])
            df_display = df[["created_at", "user_id", "question", "document_id", "is_relevant"]]
            st.dataframe(df_display, use_container_width=True)
        else:
            st.info("No query history found.")

    except requests.exceptions.RequestException as e:
        st.error(f"Failed to load history: {e}")

# --- System Analytics Tab ---
with tab4:
    st.header("System-Wide Analytics")
    try:
        with st.spinner("Loading analytics data..."):
            analytics_data = get_system_analytics()

        if analytics_data:
            st.subheader("Total Queries Per Day")
            df = pd.DataFrame(analytics_data)
            df['date'] = pd.to_datetime(df['date'])
            st.bar_chart(df.set_index('date')['queries'])
        else:
            st.info("No query data available to generate analytics.")

    except requests.exceptions.RequestException as e:
        st.error(f"Failed to load analytics data: {e}")
