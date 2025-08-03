# Owner's Guide: Advanced RAG System (V2.0)

## 1. Introduction

Welcome, Project Owner. This guide provides a comprehensive technical deep-dive into the Advanced RAG System. Version 2.0 introduces significant new capabilities for data integration and resource management.

---

## 2. System Architecture & V2.0 Enhancements

The core architecture remains a decoupled FastAPI backend and Streamlit frontend. V2.0 enhances this by adding new services and models to support external data sources.

### 2.1. New V2.0 Components
*   **Google Drive Integration:**
    *   **OAuth 2.0 Flow (`auth.py`):** New endpoints (`/google/login`, `/google/callback`) manage the secure connection to a user's Google account. User credentials (access and refresh tokens) are stored in a new `google_credentials` JSON column on the `users` table.
    *   **Google Drive Service (`services/google_drive.py`):** This new service encapsulates all interactions with the Google Drive API, using the stored user credentials.
    *   **Mapping Model (`models/gdrive_mapping.py`):** A new `GoogleDriveFolderMapping` table links an internal `Category` to an external Google Drive folder ID, enabling the "read-on-the-fly" feature.
*   **Storage Quotas:**
    *   **Database Changes:** The `documents` table now has a `size` column, and the `users` table has a `storage_used` column to track consumption in bytes.
    *   **Environment Configuration:** A new `USER_STORAGE_LIMIT_MB` variable in the `.env` file sets a universal storage limit for all users.
    *   **Backend Enforcement:** The `upload` and `ingest` endpoints now perform checks against this quota before saving files.

### 2.2. Updated Data Flows

*   **Ingestion from Google Drive:** A user can now browse their Drive and select files to ingest. The backend uses the `GoogleDriveService` to download the file and the `CloudStorageService` to upload it to the application's managed GCS bucket. The process then follows the standard ingestion flow.
*   **Read-on-the-fly Query:** When a user queries a category mapped to a Drive folder, the `query` endpoint uses the `GoogleDriveService` to temporarily download all files in that folder into memory. The `RAGSystem` has a new `query_on_the_fly` method that creates an ephemeral vector store for this content, performs the query, and then discards the data.

---

## 3. Configuration

### 3.1. Environment Variables (`.env`)
In addition to the previous variables, V2.0 requires:
*   **`USER_STORAGE_LIMIT_MB`:** Sets the universal user storage quota in megabytes.
*   **Google OAuth Credentials:** You must create a `client_secrets.json` file in the root directory with your project's OAuth 2.0 client ID and secret from the Google Cloud Console.

---

## 4. Extending the System

The new services provide a clear pattern for adding more external data sources in the future (e.g., Dropbox, OneDrive, Confluence). This would involve:
1.  Implementing the OAuth flow for the new service.
2.  Creating a new data service (e.g., `dropbox_service.py`) with `list_files` and `download_file` methods.
3.  Adding the necessary UI components for connection and browsing.

... (rest of the guide remains similar) ...
