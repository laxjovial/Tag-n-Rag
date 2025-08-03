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
