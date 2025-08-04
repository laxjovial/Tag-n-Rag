
# Advanced RAG System - Version 2.0

## Overview

This project is a sophisticated, standalone Retrieval-Augmented Generation (RAG) system designed to provide intelligent answers from a collection of documents. It features a FastAPI backend for robust API services and a Streamlit frontend for an interactive user experience.

Version 2.0 introduces powerful new capabilities, allowing the system to act as a central hub that can connect directly to a user's external data sources, such as Google Drive, reducing the need to upload and store files on the application's own storage.

## Key Features

### Core V1.0 Features
*   **Secure, Multi-Tenant Design:** Clear separation between `user` and `admin` roles with personal data isolation.
*   **Flexible Document Creation:** Upload files (PDF, DOCX, TXT) or create documents from raw text.
*   **Advanced Document Management:** Edit and export documents, set expiration policies, and organize content with personal categories.
*   **Intelligent Querying:** Query single or multiple documents/categories, view personal query history, and configure LLM settings.
*   **User and Admin Dashboards:** Dedicated interfaces for personal analytics and system-wide administration.
*   **Configurable Storage Quotas:** A universal storage limit for all users' uploaded documents, configured via environment variables.

### New in Version 2.0
*   **Direct Google Drive Integration:**
    *   **Secure Connection:** Users can securely connect their Google Drive account using OAuth 2.0.
    *   **Two Query Modes:**
        1.  **Upload from Drive:** Browse your Google Drive from within the app and select files to upload/ingest into the application's managed storage. These files are then available permanently for querying.
        2.  **Read-on-the-fly:** Query files directly from your Google Drive without uploading them. The file content is fetched temporarily for the query and is never stored on our servers, ensuring privacy.
    *   **Category Mapping:** Map categories within the application to specific folders in your Google Drive to easily query entire collections of files in "read-on-the-fly" mode.


# Advanced RAG System

## Overview

This project is a sophisticated, standalone Retrieval-Augmented Generation (RAG) system designed to provide intelligent answers from a collection of documents. It features a FastAPI backend for robust API services and a Streamlit frontend for an interactive user experience. The system is built with a strong emphasis on security, featuring a clear distinction between user and administrator roles. Users can upload, manage, and query their own documents, while administrators have access to system-wide monitoring and configuration tools.

## Key Features

*   **Secure, Multi-Tenant Design:**
    *   **Role-Based Access Control:** A clear separation between `user` and `admin` roles. Users only have access to their own data and features.
    *   **Personal Data Isolation:** All user-generated content, including documents, query history, and categories, is strictly isolated to the owning user.
*   **Flexible Document Creation:**
    *   **File Upload:** Upload multiple documents at once (PDF, DOCX, TXT).
    *   **Create from Text:** Paste or type raw text and save it as a new document.
*   **Advanced Document Management:**
    *   **Cloud Storage:** All documents are securely stored in Google Cloud Storage.
    *   **Personal Categorization:** Organize documents into personal, user-defined categories.
    *   **Editing & Exporting:** Edit any document's content and export it to PDF, DOCX, or TXT at any time.
    *   **Expiration Policies:** Set custom or default expiration dates for documents.
*   **Intelligent Querying:**
    *   **Flexible Querying:** Query individual documents, multiple documents, or entire categories at once.
    *   **Personal Query History:** Access a complete, private history of all past queries.
    *   **Configurable Generation:** Choose between different Large Language Models (LLMs) or external APIs for answer generation.
*   **User and Admin Dashboards:**
    *   **User Authentication:** Secure user registration and login system.
    *   **Personal Analytics:** A dedicated dashboard for users to view their own usage statistics.
    *   **Admin Dashboard:** A secure, admin-only interface for managing users, viewing system configurations, and monitoring global query history and analytics.



## Technology Stack

*   **Backend:** FastAPI
*   **Frontend:** Streamlit
*   **Databases:**
    *   **PostgreSQL:** For metadata, user data, query history, and system configurations.
    *   **ChromaDB:** For vector storage and similarity search.



*   **Core Libraries:** Langchain, SQLAlchemy, Google API Client Library.

## Getting Started

(Setup instructions remain the same as V1.0, but will require additional setup for Google OAuth credentials in `client_secrets.json`)

... (rest of setup guide) ...


*   **Core Libraries:** Langchain, SQLAlchemy, Psycopg2, Passlib (for hashing).

## Getting Started

This guide will walk you through setting up and running the application on your local machine.

### 1. Prerequisites
-   Python 3.9+
-   `pip` for dependency management.
-   An OpenAI API key (or another LLM provider's key).
-   Google Cloud SDK `gcloud` authenticated, with a GCS bucket created.

### 2. Step-by-Step Setup

**Step 1: Clone the Repository**
```bash
git clone <repository-url>
cd new_rag_system
```

**Step 2: Set Up a Virtual Environment**
It is highly recommended to use a virtual environment to manage dependencies.
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

**Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Step 4: Configure Your Environment**
1.  Make a copy of the example environment file:
    ```bash
    cp .env.example .env
    ```
2.  Open the `.env` file in a text editor.
3.  **`DATABASE_URL`**: For local development, the default SQLite database is fine. For production, change this to your PostgreSQL connection string.
4.  **`SECRET_KEY`**: Generate a new secret key by running `openssl rand -hex 32` in your terminal and paste the result here.
5.  **`OPENAI_API_KEY`**: Add your API key for OpenAI or any other LLM provider you plan to use.
6.  **`CLOUD_STORAGE_BUCKET`**: Enter the name of the Google Cloud Storage bucket you created.

**Step 5: Run the Backend Server**
Open a terminal and run the following command from the `new_rag_system` directory:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
The API will be running at `http://localhost:8000`.

**Step 6: Run the Frontend Application**
Open a **new** terminal and run the following command from the `new_rag_system` directory:
```bash
streamlit run app.py
```
You can now access the web application by navigating to `http://localhost:8501` in your browser.


