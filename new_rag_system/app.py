import streamlit as st
import requests

# --- Configuration ---
API_BASE_URL = "http://localhost:8000"

st.set_page_config(page_title="RAG System", layout="wide")

def login(username, password):
    """Attempt to log in and return the token."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            data={"username": username, "password": password}
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.exceptions.RequestException as e:
        st.error(f"Login failed: {e.response.json().get('detail', 'Unknown error')}")
        return None

def main():
    st.title("Welcome to the Advanced RAG System")

    if 'token' not in st.session_state:
        st.session_state.token = None

    if st.session_state.token is None:
        st.header("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                token = login(username, password)
                if token:
                    st.session_state.token = token
                    st.rerun()
    else:
        st.success("You are logged in!")
        st.write("Select a page from the sidebar to get started.")

        if st.button("Logout"):
            st.session_state.token = None
            st.rerun()

if __name__ == "__main__":
    main()
