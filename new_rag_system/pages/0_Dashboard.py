import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard", layout="wide")

st.title("Your Dashboard")

if 'token' not in st.session_state or st.session_state.token is None:
    st.warning("Please log in to view your dashboard.")
else:
    # --- Quick Stats (Placeholder) ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Documents", "15", "2 new")
    col2.metric("Total Categories", "4")
    col3.metric("Unread Notifications", "3")

    st.markdown("---")

    # --- Management Tabs ---
    tab1, tab2, tab3 = st.tabs(["My Documents", "My Categories", "My Notifications"])

    with tab1:
        st.header("Manage Your Documents")
        # This would be populated by an API call
        docs_data = {
            "Filename": ["report_q1.pdf", "legal_contract.docx"],
            "Categories": ["Quarterly Reports", "Legal"],
            "Expires At": ["2025-12-31", "N/A"],
        }
        docs_df = pd.DataFrame(docs_data)
        st.dataframe(docs_df, use_container_width=True)
        st.button("Edit Selected Document") # Placeholder for functionality

    with tab2:
        st.header("Manage Your Categories")
        # This would be populated by an API call
        cats_data = {
            "Category Name": ["Quarterly Reports", "Legal", "Medical Research"],
            "Document Count": [5, 3, 7],
        }
        cats_df = pd.DataFrame(cats_data)
        st.dataframe(cats_df, use_container_width=True)
        st.text_input("New Category Name")
        st.button("Create Category")

    with tab3:
        st.header("Your Notifications")
        # This would be populated by an API call
        st.info("Your document 'report_q1.pdf' is set to expire on 2025-12-31.", icon="ℹ️")
        st.info("Your document 'old_notes.txt' has expired and been deleted.", icon="ℹ️")
        st.button("Mark all as read")
