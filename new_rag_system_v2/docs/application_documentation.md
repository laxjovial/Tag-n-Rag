# Application Documentation: Advanced RAG System (V2.0)

## 1. Introduction
This document provides a high-level overview of the architecture, data flow, and key components of the Advanced RAG System. It is intended to be a central reference for developers and project owners to understand how the system works.

---

## 2. Architecture Overview

The system uses a modern, decoupled architecture. Version 2.0 introduces the ability to connect to external data sources like Google Drive.

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
