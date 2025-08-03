import streamlit as st
import pandas as pd
import requests
from app.utils import check_admin_auth

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
            df_display = df[["id", "username", "role", "theme"]]
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
