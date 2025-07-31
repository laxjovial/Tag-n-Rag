import streamlit as st
import pandas as pd
import requests
from typing import List, Dict

st.set_page_config(page_title="Dashboard", layout="wide")

API_BASE_URL = "http://localhost:8000"

# --- API Functions ---
@st.cache_data(ttl=300) # Cache data for 5 minutes
def get_dashboard_data(token: str) -> Dict:
    headers = {"Authorization": f"Bearer {token}"}
    docs = requests.get(f"{API_BASE_URL}/documents/", headers=headers).json()
    cats = requests.get(f"{API_BASE_URL}/categories/", headers=headers).json()
    notifs = requests.get(f"{API_BASE_URL}/notifications/", headers=headers).json()
    return {"documents": docs, "categories": cats, "notifications": notifs}

def create_category(token: str, name: str):
    headers = {"Authorization": f"Bearer {token}"}
    requests.post(f"{API_BASE_URL}/categories/", json={"name": name}, headers=headers).raise_for_status()
    st.cache_data.clear() # Clear cache after mutation

def delete_category(token: str, cat_id: int):
    headers = {"Authorization": f"Bearer {token}"}
    requests.delete(f"{API_BASE_URL}/categories/{cat_id}", headers=headers).raise_for_status()
    st.cache_data.clear()

def mark_notification_read(token: str, notif_id: int):
    headers = {"Authorization": f"Bearer {token}"}
    requests.post(f"{API_BASE_URL}/notifications/{notif_id}/read", headers=headers).raise_for_status()
    st.cache_data.clear()

def update_theme(token: str, theme: str):
    headers = {"Authorization": f"Bearer {token}"}
    requests.put(f"{API_BASE_URL}/user/profile/theme", json={"theme": theme}, headers=headers).raise_for_status()
    st.session_state.theme = theme

st.title("Your Dashboard")

if 'token' not in st.session_state or st.session_state.token is None:
    st.warning("Please log in to view your dashboard.")
else:
    try:
        data = get_dashboard_data(st.session_state.token)
        docs = data["documents"]
        cats = data["categories"]
        notifs = data["notifications"]

        # --- Quick Stats ---
        unread_notifs = len([n for n in notifs if not n['is_read']])
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Documents", len(docs))
        col2.metric("Total Categories", len(cats))
        col3.metric("Unread Notifications", unread_notifs)
        st.markdown("---")

        # --- Management Tabs ---
        tab1, tab2, tab3, tab4 = st.tabs(["My Documents", "My Categories", "My Notifications", "Settings"])

        with tab1:
            st.header("Manage Your Documents")
            if docs:
                for doc in docs:
                    with st.container(border=True):
                        st.subheader(doc['original_filename'])
                        st.caption(f"Created: {pd.to_datetime(doc['created_at']).strftime('%Y-%m-%d %H:%M')}")
                        b1, b2, b3, b4 = st.columns(4)
                        b1.page_link("pages/7_Edit_Document.py", label="Edit", icon="✏️", query_params={"doc_id": doc['id']})
                        # Export buttons and delete would go here
            else:
                st.info("You have no documents.")

        with tab2:
            st.header("Manage Your Categories")
            for cat in cats:
                cat_col1, cat_col2 = st.columns([4, 1])
                cat_col1.write(cat['name'])
                if cat_col2.button("Delete", key=f"del_cat_{cat['id']}"):
                    delete_category(st.session_state.token, cat['id'])
                    st.rerun()

            with st.form("new_cat_form", clear_on_submit=True):
                new_cat_name = st.text_input("New Category Name")
                if st.form_submit_button("Create Category"):
                    if new_cat_name:
                        create_category(st.session_state.token, new_cat_name)
                        st.rerun()

        with tab3:
            st.header("Your Notifications")
            if notifs:
                for n in notifs:
                    if n['is_read']:
                        st.write(f"~~{n['message']}~~")
                    else:
                        notif_col1, notif_col2 = st.columns([4, 1])
                        notif_col1.info(n['message'], icon="ℹ️")
                        if notif_col2.button("Mark as Read", key=f"read_{n['id']}"):
                            mark_notification_read(st.session_state.token, n['id'])
                            st.rerun()
            else:
                st.info("You have no notifications.")

        with tab4:
            st.header("Display Settings")
            theme = st.selectbox("Choose your theme", ["light", "dark"], index=0 if st.session_state.get('theme', 'light') == 'light' else 1)
            if st.button("Save Theme"):
                update_theme(st.session_state.token, theme)
                st.success(f"Theme changed to {theme}!")
                st.rerun()

    except requests.exceptions.RequestException as e:
        st.error(f"An API error occurred: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
