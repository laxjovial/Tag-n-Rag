import streamlit as st

st.set_page_config(page_title="Upload Documents", layout="wide")

st.title("Upload New Documents")

st.write("This page is under construction. Here you will be able to upload your documents.")

# Placeholder for the upload form
with st.form("upload_form", clear_on_submit=True):
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"])
    st.date_input("Expiration Date (Optional)")
    st.selectbox("Upload as new version of (Optional)", ["None"])
    submitted = st.form_submit_button("Upload")
    if submitted:
        if uploaded_file is not None:
            st.success(f"File '{uploaded_file.name}' uploaded successfully!")
        else:
            st.error("Please select a file to upload.")
