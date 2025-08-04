import streamlit as st
import os

st.set_page_config(page_title="Legal Information", layout="wide")

st.title("Legal & Policy Documents")

LEGAL_DIR = "legal"

def read_markdown_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Could not find the document at `{filepath}`."

tab1, tab2 = st.tabs(["Privacy Policy", "Terms of Service"])

with tab1:
    st.header("Privacy Policy")
    policy_content = read_markdown_file(os.path.join(LEGAL_DIR, "privacy_policy.md"))
    st.markdown(policy_content, unsafe_allow_html=True)

with tab2:
    st.header("Terms of Service")
    terms_content = read_markdown_file(os.path.join(LEGAL_DIR, "terms_of_service.md"))
    st.markdown(terms_content, unsafe_allow_html=True)
