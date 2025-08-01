import streamlit as st
import requests

# --- Configuration ---
API_BASE_URL = "http://127.0.0.1:8000"

def apply_theme(theme):
    # This is a basic way to set the theme. Streamlit's theming is limited.
    # A more robust solution might involve custom CSS.
    if theme == "dark":
        st._config.set_option('theme.base', 'dark')
    else:
        st._config.set_option('theme.base', 'light')

def login(username, password):
    try:
        response = requests.post(f"{API_BASE_URL}/auth/login", data={"username": username, "password": password})
        response.raise_for_status() # This will raise an HTTPError for bad responses (4xx or 5xx)
        token = response.json()["access_token"]

        # Fetch user profile to get theme
        headers = {"Authorization": f"Bearer {token}"}
        user_profile_response = requests.get(f"{API_BASE_URL}/user/me", headers=headers)
        user_profile_response.raise_for_status() # Raise for errors on user profile fetch
        user_profile = user_profile_response.json()

        return token, user_profile.get("theme", "light")
    except requests.exceptions.RequestException as e:
        st.error(f"Login failed: {e}")
        if e.response is not None:
            try:
                error_detail = e.response.json().get('detail', 'No detail provided.')
                st.error(f"Server response: {error_detail}")
            except requests.exceptions.JSONDecodeError:
                st.error(f"Server returned non-JSON response: {e.response.text}")
        return None, None

def register(username, password):
    try:
        response = requests.post(f"{API_BASE_URL}/auth/register", json={"username": username, "password": password})
        response.raise_for_status() # This will raise an HTTPError for bad responses (4xx or 5xx)
        st.success("Registration successful! You can now log in.")
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Registration failed: {e}")
        if e.response is not None:
            try:
                error_detail = e.response.json().get('detail', 'No detail provided.')
                st.error(f"Server response: {error_detail}")
            except requests.exceptions.JSONDecodeError:
                st.error(f"Server returned non-JSON response: {e.response.text}")
        return False

# --- Main App ---
st.set_page_config(page_title="RAG System", layout="wide")

# Apply theme if user is logged in
if 'theme' in st.session_state:
    apply_theme(st.session_state.theme)

st.title("Welcome to the Advanced RAG System")

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
                token, theme = login(username, password)
                if token:
                    st.session_state.token = token
                    st.session_state.theme = theme
                    st.rerun()
                # else:  The error message is now handled inside the login function
    with register_tab:
        with st.form("register_form"):
            reg_username = st.text_input("Choose a Username")
            reg_password = st.text_input("Choose a Password", type="password")
            agree = st.checkbox("I agree to the Terms of Service and Privacy Policy.")
            if st.form_submit_button("Register"):
                if agree:
                    register(reg_username, reg_password)
                else:
                    st.warning("You must agree to the terms to register.")
else:
    st.sidebar.success("You are logged in!")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

# --- Footer ---
st.markdown("---")
# Removed 'query_params' as it's not supported in all Streamlit versions for st.page_link
st.page_link("pages/6_Legal.py", label="Legal & Policies")
