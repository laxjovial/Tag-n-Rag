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
    return {"Authorization": f"Bearer {st.session_state.token}"}

@st.cache_data(ttl=30)
def get_all_users():
    response = requests.get(f"{API_BASE_URL}/admin/users/", headers=get_auth_headers())
    response.raise_for_status()
    return response.json()

def invite_user(username: str, email: str):
    # ... (same as before)
    pass

def delete_user(user_id: int):
    # ... (same as before)
    pass

def update_user_role(user_id: int, new_role: str):
    # ... (same as before)
    pass

@st.cache_data(ttl=15) # Shorter cache for logs
def get_audit_log(skip: int = 0, limit: int = 50):
    params = {"skip": skip, "limit": limit}
    response = requests.get(f"{API_BASE_URL}/admin/audit-log/", headers=get_auth_headers(), params=params)
    response.raise_for_status()
    return response.json()

def format_bytes(size_bytes):
    # ... (same as before)
    pass

# --- UI Rendering ---
st.title("Admin Dashboard")

tabs = ["User Management", "LLM/API Configs", "Global History", "System Analytics", "Audit Log"]
tab1, tab2, tab3, tab4, tab5 = st.tabs(tabs)

# --- User Management Tab ---
with tab1:
    # ... (same as before)
    pass

# --- Audit Log Tab ---
with tab5:
    st.header("System Audit Log")

    if 'audit_log_page' not in st.session_state:
        st.session_state.audit_log_page = 0

    try:
        skip = st.session_state.audit_log_page * 50
        with st.spinner("Loading audit logs..."):
            log_data = get_audit_log(skip=skip, limit=50)

        if not log_data:
            st.info("No audit log entries found.")
            if st.session_state.audit_log_page > 0:
                st.warning("You are on a page with no results. Go back to the previous page.")
        else:
            df = pd.DataFrame(log_data)
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')

            df_display = df[["timestamp", "username", "action", "details"]]
            st.dataframe(df_display, use_container_width=True)

        # --- Pagination ---
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("⬅️ Previous Page", disabled=(st.session_state.audit_log_page == 0)):
                st.session_state.audit_log_page -= 1
                st.rerun()
        with col3:
            if st.button("Next Page ➡️", disabled=(len(log_data) < 50)):
                st.session_state.audit_log_page += 1
                st.rerun()

    except requests.exceptions.RequestException as e:
        st.error(f"Failed to load audit logs: {e}")

# --- Other Tabs (placeholders) ---
with tab2:
    st.header("Manage LLM and API Configurations")
    st.info("This section is under construction.")
with tab3:
    st.header("Global Query History")
    st.info("This section is under construction.")
with tab4:
    st.header("System-Wide Analytics")
    st.info("This section is under construction.")
