import streamlit as st

st.set_page_config(page_title="Query Documents", layout="wide")

st.title("Query Your Documents")

st.write("This page is under construction. Here you will be able to ask questions to your documents.")

# Placeholder for the query interface
with st.sidebar:
    st.header("Select Documents")
    st.checkbox("report_q1.pdf")
    st.checkbox("legal_contract.docx")
    st.checkbox("notes.txt")

    st.header("Settings")
    st.selectbox("Model", ["OpenAI GPT-4", "Anthropic Claude 2"])
    st.slider("Temperature", 0.0, 1.0, 0.7)

st.text_area("Ask a question...")
if st.button("Get Answer"):
    with st.spinner("Thinking..."):
        st.info("This is a placeholder answer based on your question.")
