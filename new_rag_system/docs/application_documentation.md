# Application Documentation: Advanced RAG System

## 1. Introduction
This document provides a high-level overview of the architecture, data flow, and key components of the Advanced RAG System. It is intended to be a central reference for developers and project owners to understand how the system works.

---

## 2. Architecture Overview

The system is designed with a modern, decoupled architecture that separates the frontend, backend, and data storage layers.

```
+------------------+      +------------------+      +-------------------------+
| Streamlit        | <--> | FastAPI          | <--> | PostgreSQL              |
| (Frontend)       |      | (Backend API)    |      | (Metadata, Users, Logs) |
+------------------+      +------------------+      +-------------------------+
                             |
                             |      +-------------------------+
                             +----->| ChromaDB                |
                             |      | (Vector Store)          |
                             |      +-------------------------+
                             |
                             |      +-------------------------+
                             +----->| Google Cloud Storage    |
                                    | (Document Files)        |
                                    +-------------------------+
```

*   **Frontend (Streamlit):** A multi-page web application that provides the user interface.
*   **Backend (FastAPI):** A RESTful API that handles all business logic, data processing, and communication with the data stores.
*   **Data Stores:**
    *   **PostgreSQL:** The primary relational database for storing structured data like user accounts, document metadata, categories, and query history.
    *   **ChromaDB:** A specialized vector database for storing document embeddings and performing efficient similarity searches.
    *   **Google Cloud Storage (GCS):** A scalable object store for persisting the original uploaded document files.

---

## 3. Data Flow

### 3.1. Document Ingestion Flow

1.  **Document Creation:** A user creates a document in one of three ways:
    *   **File Upload:** Uploading files via the UI.
    *   **From Text:** Pasting raw text into the UI.
    *   **From Query:** Saving a query result as a new document.
2.  **API Request:** The frontend sends a POST request to the appropriate FastAPI backend endpoint (e.g., `/documents/upload`, `/documents/from_text`).
3.  **Store in GCS:** The backend saves the document content to a new file in a GCS bucket with a unique filename.
4.  **Create Metadata:** A new `Document` record is created in the PostgreSQL database with the file's metadata.
5.  **Process & Embed:** The document's content is processed and embedded by the `RAGSystem`.
6.  **Store in Vector DB:** The embeddings are stored in ChromaDB.

### 3.2. Query Lifecycle

1.  **User Query:** A user selects documents or a category and submits a question through the Streamlit UI.
2.  **API Request:** The frontend sends a POST request to the FastAPI backend (`/query`).
3.  **Fetch Document IDs:** If a category is queried, the backend first fetches all document IDs belonging to that category from PostgreSQL.
4.  **Retrieve Context:** The `RAGSystem` takes the user's question and the relevant document IDs. It creates an embedding of the question and queries ChromaDB to find the most relevant document chunks.
5.  **Generate Answer:** The retrieved chunks (the "context") and the original question are passed to a large language model (LLM) via Langchain.
6.  **Return Response:** The LLM generates an answer, which is sent back through the API to the frontend and displayed to the user.
7.  **Log Query:** The query and its context are logged in the `query_logs` table in PostgreSQL.

---

## 4. Key Components & Services

*   **`app/main.py`:** The entry point for the FastAPI application. It initializes the app, includes the API routers, and starts background services.
*   **`app/api/`:** This directory contains the API routers, with each file corresponding to a different resource (e.g., `documents.py`, `users.py`).
*   **`app/services/`:**
    *   **`rag.py` (`RAGSystem`):** The core of the application's intelligence. It handles all the logic for processing and querying documents.
    *   **`storage.py` (`CloudStorageService`):** A service dedicated to interacting with Google Cloud Storage.
    *   **`expiration.py`:** A background service that runs periodically to handle document expiration and send notifications.
*   **`app/database.py`:** Sets up the database connection and session management.
*   **`app/models/`:** Contains all the SQLAlchemy database models.
*   **`app.py` (root):** The main entry point for the Streamlit frontend application.
*   **`pages/`:** Contains the individual pages of the Streamlit application.
