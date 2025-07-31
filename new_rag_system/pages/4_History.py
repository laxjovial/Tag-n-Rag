import streamlit as st
import pandas as pd

st.set_page_config(page_title="Query History", layout="wide")

st.title("Your Query History")

st.write("This page is under construction. Here you will be able to see your past queries.")

# Placeholder for the history list
data = {
    "Timestamp": ["2024-07-15 10:30", "2024-07-15 10:25", "2024-07-14 11:00"],
    "Question": ["What were the key findings in the Q3 report?", "What is the termination clause?", "Summarize the notes."],
    "Queried Documents": ["report_q1.pdf", "legal_contract.docx", "notes.txt"],
}
df = pd.DataFrame(data)

st.dataframe(df, use_container_width=True)
