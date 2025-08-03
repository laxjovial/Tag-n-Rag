
# Application Documentation: Advanced RAG System (V2.0)

# Application Documentation: Advanced RAG System


## 1. Introduction
This document provides a high-level overview of the architecture, data flow, and key components of the Advanced RAG System. It is intended to be a central reference for developers and project owners to understand how the system works.

---

## 2. Architecture Overview


The system uses a modern, decoupled architecture. Version 2.0 introduces the ability to connect to external data sources like Google Drive.

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

                             |      +-------------------------+      +------------------+
                             +----->| Cloud Storage Service   | <--> | GCS / S3         |
                             |      | (Managed Documents)     |      | (Object Store)   |
                             |      +-------------------------+      +------------------+
                             |
                             |      +-------------------------+      +------------------+
                             +----->| Google Drive Service    | <--> | Google Drive API |
                                    | (On-the-fly Documents)  |      | (User's Files)   |
                                    +-------------------------+      +------------------+
```
The architecture remains similar, but the backend now includes a dedicated service for interacting with the Google Drive API, allowing for two distinct data handling modes.

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


### 3.1. Document Ingestion Flow (Managed Storage)
This flow applies to direct uploads and ingestion from Google Drive.
1.  **Document Creation:** A user uploads a file or ingests it from Google Drive.
2.  **API Request:** The frontend sends the file/data to the FastAPI backend.
3.  **Store in GCS:** The backend saves the document content to a new file in the application's GCS bucket.
4.  **Create Metadata:** A `Document` record is created in PostgreSQL, including the file's size.
5.  **Update User Storage:** The user's `storage_used` is incremented.
6.  **Process & Embed:** The document's content is processed and embedded by the `RAGSystem`.
7.  **Store in Vector DB:** The embeddings are stored in ChromaDB for future querying.

### 3.2. Read-on-the-fly Query Lifecycle
1.  **User Query on Mapped Category:** A user selects a category that is mapped to a Google Drive folder.
2.  **API Request:** The frontend sends a POST request to `/query` with the category ID.
3.  **Check for Mapping:** The backend identifies that the category is mapped to a Drive folder.
4.  **Fetch from Google Drive:** The `GoogleDriveService` lists all files in the mapped folder and downloads their content into memory.
5.  **On-the-fly RAG:** The combined content is passed to the `RAGSystem`'s `query_on_the_fly` method. This method creates a temporary, in-memory vector store for this query only.
6.  **Generate Answer:** The retrieved context from the temporary store is passed to the LLM to generate an answer.
7.  **Return Response & Discard:** The answer is returned to the user. The temporary content and vector store are discarded. No files are stored on the server.
8.  **Log Query:** The query is logged in PostgreSQL.

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


*   **`app/services/`:**
    *   **`google_drive.py` (`GoogleDriveService`):** A new service for handling all interactions with the Google Drive API, including listing files and downloading content.
*   **`app/api/`:**
    *   **`gdrive.py`:** New endpoints for listing Google Drive files and ingesting them into managed storage.
    *   **`mappings.py`:** New endpoints for creating, listing, and deleting mappings between app categories and Google Drive folders.
*   **`app/models/`:**
    *   **`gdrive_mapping.py`:** New model to store the category-to-folder mappings.
    *   `document.py` and `user.py` have been updated to include `size` and `storage_used` columns respectively, to support storage quotas.
*   **`pages/`:**
    *   **`11_Connect_Data_Source.py`:** New page for managing the connection to Google Drive and uploading files from it.
    *   **`12_Manage_Mappings.py`:** New page for managing the category-to-folder mappings for the read-on-the-fly feature.

(Other components remain largely the same)

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

