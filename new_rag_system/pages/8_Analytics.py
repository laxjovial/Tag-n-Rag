import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Usage Analytics", layout="wide")

API_BASE_URL = "http://localhost:8000"

def get_queries_per_day(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE_URL}/admin/analytics/queries_per_day", headers=headers)
    response.raise_for_status()
    return response.json()

st.title("Usage Analytics Dashboard")

if 'token' not in st.session_state or st.session_state.token is None:
    st.warning("Please log in to view this page.")
else:
    # In a real app, we'd also check the user's role from the token or another API call
    st.write("Welcome, Admin!")

    try:
        with st.spinner("Loading analytics data..."):
            data = get_queries_per_day(st.session_state.token)

        if data:
            st.header("Queries Per Day")
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            st.bar_chart(df.set_index('date')['queries'])
        else:
            st.info("No query data available yet.")

    except requests.exceptions.RequestException as e:
        st.error(f"Failed to load analytics data: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
