# Advanced RAG System

## Overview

This project is a sophisticated, standalone Retrieval-Augmented Generation (RAG) system designed to provide intelligent answers from a collection of documents. It features a FastAPI backend for robust API services and a Streamlit frontend for an interactive user experience. The system allows users to upload, manage, and query documents with advanced features like versioning, expiration, and configurable AI models.

## Key Features

*   **Flexible Document Creation:**
    *   **File Upload:** Upload multiple documents at once (PDF, DOCX, TXT).
    *   **Create from Text:** Paste or type raw text and save it as a new document.
    *   **Save Query Results:** Save the results of your queries as new, searchable documents.
*   **Advanced Document Management:**
    *   **Cloud Storage:** All documents are securely stored in Google Cloud Storage.
    *   **Categorization:** Organize all documents into custom categories.
    *   **Editing & Exporting:** Edit any document's content and export it to PDF, DOCX, or TXT at any time.
    *   **Expiration Policies:** Set custom or default expiration dates for documents, with automatic notifications.
*   **Intelligent Querying:**
    *   **Flexible Querying:** Query individual documents, multiple documents, or entire categories at once.
    *   **Query History:** Access a complete history of all past queries.
    *   **Configurable Generation:** Choose between different Large Language Models (LLMs) or external APIs for answer generation.
*   **User and Admin Controls:**
    *   **User Authentication:** Secure user registration and login system.
    *   **LLM Controls:** Adjust LLM temperature and select models directly from the UI.
    *   **Admin Dashboard:** A dedicated interface for administrators to manage users, system configurations, and view global query history.

## Technology Stack

*   **Backend:** FastAPI
*   **Frontend:** Streamlit
*   **Databases:**
    *   **PostgreSQL:** For metadata, user data, query history, and system configurations.
    *   **ChromaDB:** For vector storage and similarity search.
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
