import streamlit as st
import pandas as pd
import requests
from typing import List, Dict

st.set_page_config(page_title="Dashboard", layout="wide")

API_BASE_URL = "http://localhost:8000"

# --- API Functions ---
def get_dashboard_data(token: str) -> Dict:
    headers = {"Authorization": f"Bearer {token}"}
    docs = requests.get(f"{API_BASE_URL}/documents/", headers=headers).json()
    cats = requests.get(f"{API_BASE_URL}/categories/", headers=headers).json()
    notifs = requests.get(f"{API_BASE_URL}/notifications/", headers=headers).json()
    return {"documents": docs, "categories": cats, "notifications": notifs}

def create_category(token: str, name: str):
    headers = {"Authorization": f"Bearer {token}"}
    requests.post(f"{API_BASE_URL}/categories/", json={"name": name}, headers=headers).raise_for_status()

def delete_category(token: str, cat_id: int):
    headers = {"Authorization": f"Bearer {token}"}
    requests.delete(f"{API_BASE_URL}/categories/{cat_id}", headers=headers).raise_for_status()

def mark_notification_read(token: str, notif_id: int):
    headers = {"Authorization": f"Bearer {token}"}
    requests.post(f"{API_BASE_URL}/notifications/{notif_id}/read", headers=headers).raise_for_status()

st.title("Your Dashboard")

if 'token' not in st.session_state or st.session_state.token is None:
    st.warning("Please log in to view your dashboard.")
else:
    try:
        with st.spinner("Loading your dashboard..."):
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
                    with st.container():
                        st.subheader(doc['original_filename'])
                        st.caption(f"Created on: {pd.to_datetime(doc['created_at']).strftime('%Y-%m-%d %H:%M')}")

                        b1, b2, b3, b4 = st.columns(4)
                        b1.page_link("pages/7_Edit_Document.py", label="Edit", icon="✏️", query_params={"doc_id": doc['id']})

                        b2.download_button(
                            label="Export as PDF",
                            data=requests.get(f"{API_BASE_URL}/documents/{doc['id']}/export?format=pdf", headers={"Authorization": f"Bearer {st.session_state.token}"}).content,
                            file_name=f"{doc['original_filename']}.pdf",
                            mime="application/pdf",
                            key=f"pdf_{doc['id']}"
                        )
                        b3.download_button(
                            label="Export as DOCX",
                            data=requests.get(f"{API_BASE_URL}/documents/{doc['id']}/export?format=docx", headers={"Authorization": f"Bearer {st.session_state.token}"}).content,
                            file_name=f"{doc['original_filename']}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key=f"docx_{doc['id']}"
                        )
                        # Add a delete button here as well
                        if b4.button("Delete", key=f"del_doc_{doc['id']}"):
                            # Add delete logic here
                            st.rerun()

                        st.markdown("---")
            else:
                st.info("You have no documents.")

        with tab2:
            # ... (existing category logic)
            pass

        with tab3:
            # ... (existing notification logic)
            pass

        with tab4:
            # ... (existing settings logic)
            pass

    except requests.exceptions.RequestException as e:
        st.error(f"An API error occurred: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
