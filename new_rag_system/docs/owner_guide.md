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
*   **Authentication:** A robust JWT-based authentication system (`auth_api.py`) secures the endpoints. Passwords are never stored in plain text; they are hashed using `passlib`.

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
*   **Cloud Storage:** For a production environment, local file storage for uploaded documents should be replaced with a cloud storage solution like Amazon S3 or Google Cloud Storage. The system includes placeholder functions for this integration.
*   **Scalability:** The backend can be scaled horizontally by running multiple instances of the FastAPI server behind a load balancer.
