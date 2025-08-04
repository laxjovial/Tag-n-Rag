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
    """Handles the login process, including API call and session state update."""
    try:
        response = requests.post(f"{API_BASE_URL}/auth/login", data={"username": username, "password": password})
        response.raise_for_status()
        token = response.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}
        user_profile_response = requests.get(f"{API_BASE_URL}/user/me", headers=headers)
        user_profile_response.raise_for_status()
        user_profile = user_profile_response.json()

        # Set session state upon successful login
        st.session_state.token = token
        st.session_state.theme = user_profile.get("theme", "light")
        st.session_state.role = user_profile.get("role", "user")
        st.session_state.username = user_profile.get("username")
        return True
    except requests.exceptions.RequestException as e:
        error_message = "Login failed."
        if e.response is not None:
            try:
                error_detail = e.response.json().get('detail')
                if error_detail:
                    error_message = f"Login failed: {error_detail}"
            except requests.exceptions.JSONDecodeError:
                error_message = "Login failed: Server returned an invalid response."
        st.error(error_message)
        return False

def register(username, password):
    """Handles the registration process."""
    try:
        response = requests.post(f"{API_BASE_URL}/auth/register", json={"username": username, "password": password})
        response.raise_for_status()
        st.success("Registration successful! You can now log in.")
        return True
    except requests.exceptions.RequestException as e:
        error_message = "Registration failed."
        if e.response is not None:
            try:
                error_detail = e.response.json().get('detail')
                if error_detail:
                    error_message = f"Registration failed: {error_detail}"
            except requests.exceptions.JSONDecodeError:
                error_message = "Registration failed: Server returned an invalid response."
        st.error(error_message)
        return False

def render_sidebar():
    """Renders the sidebar navigation based on user role."""
    st.sidebar.success(f"Logged in as **{st.session_state.username}**")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    st.sidebar.header("Navigation")
    # Use st.page_link for modern Streamlit navigation
    st.page_link("pages/0_Dashboard.py", label="Dashboard")
    st.page_link("pages/1_Upload.py", label="Upload Documents")
    st.page_link("pages/10_Create_from_Text.py", label="Create from Text")
    st.page_link("pages/2_View_Documents.py", label="View Documents")
    st.page_link("pages/3_Query.py", label="Query Documents")
    st.page_link("pages/4_History.py", label="Query History")
    st.page_link("pages/8_Analytics.py", label="My Analytics")
    st.page_link("pages/9_Export.py", label="Export Data")

    # Conditionally render Admin link
    if st.session_state.get("role") == "admin":
        st.sidebar.divider()
        st.sidebar.header("Admin")
        st.page_link("pages/5_Admin.py", label="Admin Dashboard")

    st.sidebar.divider()
    st.page_link("pages/6_Legal.py", label="Legal & Policies")


# --- Main App ---
st.set_page_config(page_title="RAG System", layout="wide")

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None

# Main logic to display login/register or the app
if st.session_state.token is None:
    st.title("Welcome to the Advanced RAG System")
    login_tab, register_tab = st.tabs(["Login", "Register"])
    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                if login(username, password):
                    st.rerun() # Rerun to apply login state
    with register_tab:
        with st.form("register_form"):
            reg_username = st.text_input("Choose a Username")
            reg_password = st.text_input("Choose a Password", type="password")
            agree = st.checkbox("I agree to the Terms of Service and Privacy Policy.")
            if st.form_submit_button("Register"):
                if agree:
                    if register(reg_username, reg_password):
                        st.info("Please log in with your new credentials.")
                else:
                    st.warning("You must agree to the terms to register.")
else:
    # Apply theme now that we know the user is logged in
    if 'theme' in st.session_state:
        apply_theme(st.session_state.theme)

    # Render the main app view
    render_sidebar()
    # You can have a main dashboard here or just direct users to the sidebar
    st.title("Dashboard")
    st.write("Select a page from the sidebar to get started.")
