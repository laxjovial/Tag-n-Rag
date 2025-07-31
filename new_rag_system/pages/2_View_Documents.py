import streamlit as st
import pandas as pd

st.set_page_config(page_title="View Documents", layout="wide")

st.title("View and Manage Your Documents")

st.write("This page is under construction. Here you will be able to see and manage your documents.")

# Placeholder for the document list
st.text_input("Search by filename")

data = {
    "Filename": ["report_q1.pdf", "legal_contract.docx", "notes.txt"],
    "Version": [2, 1, 1],
    "Expires At": ["2025-12-31", "N/A", "N/A"],
    "Created At": ["2024-07-15", "2024-07-14", "2024-07-12"],
}
df = pd.DataFrame(data)

st.dataframe(df, use_container_width=True)

st.button("Peek")
st.button("Delete")
