import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Export Results", layout="wide")

API_BASE_URL = "http://localhost:8000"

def get_history(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE_URL}/history/", headers=headers)
    response.raise_for_status()
    return response.json()

st.title("Export Query Results")

if 'token' not in st.session_state or st.session_state.token is None:
    st.warning("Please log in to export results.")
else:
    try:
        with st.spinner("Loading your query history..."):
            history = get_history(st.session_state.token)

        if not history:
            st.info("You have no query history to export.")
        else:
            st.write("Here are your past queries. Click to export.")

            for item in history:
                with st.container():
                    st.markdown(f"**Query:** `{item['query_text']}`")
                    st.caption(f"Answered on: {pd.to_datetime(item['created_at']).strftime('%Y-%m-%d %H:%M')}")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.download_button(
                            label="Export as PDF",
                            data=requests.get(f"{API_BASE_URL}/query/{item['id']}/export?format=pdf", headers={"Authorization": f"Bearer {st.session_state.token}"}).content,
                            file_name=f"query_{item['id']}.pdf",
                            mime="application/pdf"
                        )
                    with col2:
                        st.download_button(
                            label="Export as DOCX",
                            data=requests.get(f"{API_BASE_URL}/query/{item['id']}/export?format=docx", headers={"Authorization": f"Bearer {st.session_state.token}"}).content,
                            file_name=f"query_{item['id']}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                    with col3:
                        st.download_button(
                            label="Export as TXT",
                            data=requests.get(f"{API_BASE_URL}/query/{item['id']}/export?format=txt", headers={"Authorization": f"Bearer {st.session_state.token}"}).content,
                            file_name=f"query_{item['id']}.txt",
                            mime="text/plain"
                        )
                    st.markdown("---")

    except requests.exceptions.RequestException as e:
        st.error(f"Failed to load history: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
