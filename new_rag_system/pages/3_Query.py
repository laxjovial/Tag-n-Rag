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

question = st.text_area("Ask a question...")
if st.button("Get Answer"):
    with st.spinner("Thinking..."):
        # This is a placeholder for the actual API call
        st.session_state.last_answer = "This is a placeholder answer based on your question."
        st.session_state.last_question = question

if "last_answer" in st.session_state:
    st.markdown("---")
    st.subheader("Answer")
    st.write(st.session_state.last_answer)

    with st.expander("Actions"):
        st.button("Save as New Document")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.button("Export as PDF")
        with col2:
            st.button("Export as DOCX")
        with col3:
            st.button("Export as TXT")
