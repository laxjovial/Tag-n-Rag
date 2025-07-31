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

def register(username, password):
    """Attempt to register a new user."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        st.success("Registration successful! You can now log in.")
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Registration failed: {e.response.json().get('detail', 'Unknown error')}")
        return False

def main():
    st.title("Welcome to the Advanced RAG System")

    # --- Footer ---
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center;">
            <a href="/Legal" target="_self">Terms of Service</a> |
            <a href="/Legal" target="_self">Privacy Policy</a>
        </div>
        """,
        unsafe_allow_html=True
    )

    if 'token' not in st.session_state:
        st.session_state.token = None

    if st.session_state.token is None:
        login_tab, register_tab = st.tabs(["Login", "Register"])

        with login_tab:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login")
                if submitted:
                    token = login(username, password)
                    if token:
                        st.session_state.token = token
                        st.rerun()

        with register_tab:
            with st.form("register_form"):
                reg_username = st.text_input("Choose a Username")
                reg_password = st.text_input("Choose a Password", type="password")
                agree = st.checkbox("I agree to the [Terms of Service](legal/terms_of_service.md) and [Privacy Policy](legal/privacy_policy.md).")
                reg_submitted = st.form_submit_button("Register")
                if reg_submitted:
                    if agree:
                        register(reg_username, reg_password)
                    else:
                        st.warning("You must agree to the terms and policy to register.")

    else:
        st.success("You are logged in!")
        st.write("Select a page from the sidebar to get started.")

        if st.button("Logout"):
            st.session_state.token = None
            st.rerun()

if __name__ == "__main__":
    main()
