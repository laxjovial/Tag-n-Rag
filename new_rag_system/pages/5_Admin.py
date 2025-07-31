import streamlit as st
import pandas as pd

st.set_page_config(page_title="Admin Dashboard", layout="wide")

st.title("Admin Dashboard")

st.write("This page is under construction. Here you will be able to manage users and system settings.")

# Placeholder for the admin interface
tab1, tab2, tab3 = st.tabs(["User Management", "LLM/API Configs", "Global History"])

with tab1:
    st.header("Manage Users")
    st.button("Create New User")
    # Placeholder user data
    users = pd.DataFrame({
        "Username": ["admin", "user1", "user2"],
        "Role": ["admin", "user", "user"],
        "Created At": ["2024-07-10", "2024-07-11", "2024-07-12"],
    })
    st.dataframe(users, use_container_width=True)

with tab2:
    st.header("Manage LLM and API Configurations")
    st.button("Add New Configuration")
    # Placeholder config data
    configs = pd.DataFrame({
        "Name": ["OpenAI GPT-4", "Internal Summarizer"],
        "Type": ["LLM", "API"],
        "Model/Endpoint": ["gpt-4", "http://internal-api/summarize"],
        "Default": [True, False],
    })
    st.dataframe(configs, use_container_width=True)

with tab3:
    st.header("Global Query History")
    # Placeholder global history data
    history = pd.DataFrame({
        "Timestamp": ["2024-07-15 10:30", "2024-07-15 10:25"],
        "User": ["user1", "user2"],
        "Question": ["What were the key findings?", "What is the termination clause?"],
    })
    st.dataframe(history, use_container_width=True)
