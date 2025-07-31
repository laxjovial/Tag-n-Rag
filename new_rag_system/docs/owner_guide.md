# Owner's Guide: Advanced RAG System

## 1. Introduction

Welcome, Project Owner. This guide provides a comprehensive technical deep-dive into the Advanced RAG System. It is designed to give you a complete understanding of the system's architecture, configuration, and potential for future extensions.

---

## 2. System Architecture

The system is built on a modern, decoupled architecture, ensuring scalability and maintainability. It consists of a FastAPI backend, a Streamlit frontend, and a dual-database setup for structured and vector data.

### 2.1. FastAPI Backend

The backend is the core of the system, handling all business logic, data processing, and communication with the databases.

*   **API Endpoints (`/main.py`, `/api/`):** Exposes a RESTful API for the frontend to consume. Endpoints are organized by functionality (e.g., `auth_api.py`, `document_api.py`).
*   **Services (`/services/`):** Contain the business logic. For example, the `RAGService` would orchestrate the process of retrieving documents and generating answers.
*   **Database Models (`/database.py`):** Defines the SQLAlchemy models for the PostgreSQL database, representing tables for users, documents, etc.
*   **Authentication (JWT):** The system uses a robust JSON Web Token (JWT) based authentication system, implemented in `app/api/auth.py`. This ensures that all endpoints are secure and that users can only access their own data. For more details on the JWT implementation and configuration, see the `jwt_authentication.md` guide.

### 2.2. Streamlit Frontend

The frontend provides an interactive and user-friendly interface for the system.

*   **Multipage Structure (`/pages/`):** The app is organized into multiple pages (Upload, View, Query, etc.) for a clean user experience. The main `app.py` handles routing and user login.
*   **State Management:** Streamlit's session state (`st.session_state`) is used to manage user sessions, authentication tokens, and other temporary data.
*   **Backend Communication:** The frontend communicates with the backend via HTTP requests to the FastAPI endpoints.

### 2.3. Databases

*   **PostgreSQL (Structured Data):**
    *   **`users`:** Stores user credentials (username, hashed password) and roles (user, admin).
    *   **`documents`:** Stores metadata for each document, including `version`, `parent_document_id`, `owner_id`, and `expires_at`.
    *   **`query_logs`:** Logs every query made, linking to the user and the documents queried.
    *   **`llm_configs`:** Stores configurations for different LLMs and external APIs, manageable by the admin.
*   **ChromaDB (Vector Data):**
    *   This database stores the vector embeddings of the document chunks. When a query is made, ChromaDB performs a fast similarity search to find the most relevant document chunks to feed into the language model.

### 2.4. Data Flow

**Document Ingestion:**
1.  User uploads a file via the Streamlit UI.
2.  The backend receives the file, extracts the text, and splits it into manageable chunks.
3.  The text chunks are converted into vector embeddings using a sentence-transformer model.
4.  These embeddings are stored in ChromaDB.
5.  Document metadata (filename, version, owner, etc.) is saved in the PostgreSQL database.

**Query Process:**
1.  User submits a query for a set of selected documents.
2.  The backend converts the user's query into a vector embedding.
3.  A similarity search is performed in ChromaDB against the vectors of the selected documents.
4.  The most relevant document chunks are retrieved.
5.  The query and the retrieved chunks are passed to the configured LLM or API.
6.  The generated answer is returned to the user. The query and its context are logged in PostgreSQL.

---

## 3. Configuration

The system is highly configurable via environment variables and a YAML configuration file.

### 3.1. Environment Variables (`.env`)

A `.env` file is required to store sensitive information. Key variables include:

*   `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `DATABASE_URL`
*   `SECRET_KEY` (for JWT token signing)
*   `ALGORITHM` (e.g., HS256)
*   `ACCESS_TOKEN_EXPIRE_MINUTES`
*   `OPENAI_API_KEY` (and other LLM provider keys)

### 3.2. LLM/API Configuration (`config.yml`)

The `config.yml` file allows admins to define the available LLMs and APIs for the generation step.

**Example `config.yml`:**
```yaml
llm_providers:
  - name: "OpenAI GPT-4"
    model: "gpt-4"
    api_key_env: "OPENAI_API_KEY"
    default_temp: 0.7
  - name: "Anthropic Claude 2"
    model: "claude-2"
    api_key_env: "ANTHROPIC_API_KEY"
    default_temp: 0.5

api_providers:
  - name: "Internal Summarizer"
    endpoint: "http://internal-api:8080/summarize"
    auth_token_env: "INTERNAL_API_TOKEN"
```

---

## 4. Extending the System

The modular architecture makes it straightforward to extend the system.

### 4.1. Adding a New API Endpoint

1.  Define the Pydantic models for request/response in `models.py`.
2.  Create the business logic for the new feature in a relevant service file in `/services/`.
3.  Add the new endpoint to a router in `/api/`. Ensure you include dependency injection for services and authentication.

### 4.2. Adding a New Frontend Page

1.  Create a new Python file in the `/pages` directory (e.g., `6_New_Feature.py`).
2.  Streamlit will automatically pick it up and add it to the sidebar.
3.  Implement the UI and the logic to call the corresponding backend endpoints.

### 4.3. Supporting a New Document Type

1.  Identify a Python library that can extract text from the new file format.
2.  In the document ingestion service, add logic to detect the new file type (e.g., by extension).
3.  Use the chosen library to extract the text before passing it to the chunking and vectorization process.

---

## 5. Deployment Considerations

*   **Containerization:** The entire application (backend, frontend, databases) is designed to be easily containerized using Docker and managed with Docker Compose for development and production.
*   **Cloud Storage (Google Cloud Storage):** The system is now fully integrated with GCS for persistent and scalable document storage. The `CloudStorageService` in `app/services/storage.py` handles all interactions with the GCS API.
    *   **Configuration:** To enable GCS, you must set the `CLOUD_STORAGE_BUCKET` environment variable in your `.env` file. You must also ensure that the application's environment has the necessary GCS credentials (e.g., by setting the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to your service account key file).
*   **Scalability:** The backend can be scaled horizontally by running multiple instances of the FastAPI server behind a load balancer.

---

## 6. Setup and Running Instructions

This guide will walk you through setting up and running the application on your local machine.

### 6.1. Prerequisites
-   Python 3.9+
-   `pip` for dependency management.
-   An OpenAI API key (or another LLM provider's key).
-   Google Cloud SDK `gcloud` authenticated, with a GCS bucket created.

### 6.2. Step-by-Step Setup

**Step 1: Clone the Repository**
```bash
git clone <repository-url>
cd new_rag_system
```

**Step 2: Set Up a Virtual Environment**
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
3.  **`DATABASE_URL`**: For production, change this to your PostgreSQL connection string.
4.  **`SECRET_KEY`**: Generate a new secret key by running `openssl rand -hex 32`.
5.  **`OPENAI_API_KEY`**: Add your API key for OpenAI or any other provider.
6.  **`CLOUD_STORAGE_BUCKET`**: Enter the name of your GCS bucket.

**Step 5: Run the Backend & Frontend**
-   **Backend:** `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
-   **Frontend:** `streamlit run app.py`

You can now access the web application at `http://localhost:8501`.

## 6. New Features Details

### 6.1. Default Expiration and Notifications
*   **Default Expiration:** The system supports a system-wide default expiration period for documents. This is stored in the `settings` table in the database with the key `default_expiration_days`. Admins can set this value.
*   **Notification Service:** The background service in `app/services/expiration.py` now also checks for documents that are nearing their expiration date. When a document is found, a `Notification` object is created in the database for the document's owner.

### 6.2. Document Categorization
*   **Database:** A many-to-many relationship has been established between `documents` and `categories` tables, linked by the `document_category` association table. The `User` model now includes a `theme` preference.
*   **API:** The API has been expanded with endpoints for managing user profiles (`/user`), handling document edits, exporting queries, and saving queries as new documents.
*   **LLM Flexibility:** The `RAGSystem` has been refactored to dynamically load LLM configurations, allowing for seamless integration with any Langchain-compatible model, including local models served via an API like Ollama. Refer to `llm_integration_guide.md` for detailed instructions.
