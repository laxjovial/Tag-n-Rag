import io
import pypdf
import docx
import streamlit as st

def read_file_content(file) -> str:
    """
    Reads the content of a file-like object and returns it as a string.
    Supports PDF, DOCX, and TXT files.
    """
    content = ""
    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        pdf_reader = pypdf.PdfReader(file.file)
        for page in pdf_reader.pages:
            content += page.extract_text() or ""
    elif filename.endswith(".docx"):
        doc = docx.Document(file.file)
        for para in doc.paragraphs:
            content += para.text + "\n"
    elif filename.endswith(".txt"):
        content = file.file.read().decode("utf-8")
    else:
        # For other file types, you might want to raise an exception
        # or handle them differently.
        raise ValueError(f"Unsupported file type: {filename}")

    return content

def check_auth(page_name="this page"):
    """
    Checks if the user is logged in (i.e., if a token exists in the session state).
    If not, it displays a warning, a link to the login page, and stops the script.
    """
    if 'token' not in st.session_state or st.session_state.token is None:
        st.warning(f"You must be logged in to access {page_name}.")
        st.page_link("app.py", label="Go to Login Page", icon="🔒")
        st.stop()

def check_admin_auth():
    """
    Performs a full authentication and authorization check for admin pages.
    It ensures the user is logged in and that their role is 'admin'.
    If either check fails, it stops the script with an appropriate message.
    """
    # First, ensure the user is logged in at all.
    check_auth(page_name="the admin dashboard")

    # Next, check if the logged-in user has the 'admin' role.
    if st.session_state.get("role") != "admin":
        st.error("Access Denied: You do not have the required permissions for this page.")
        st.info("If you believe this is an error, please contact your system administrator.")
        st.page_link("pages/0_Dashboard.py", label="Return to Dashboard", icon="🏠")
        st.stop()
