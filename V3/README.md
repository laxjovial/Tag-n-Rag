# Advanced RAG System - Version 3.0

## Overview

This project is a sophisticated, enterprise-grade Retrieval-Augmented Generation (RAG) system designed to provide intelligent answers from a variety of data sources. It features a scalable FastAPI backend, an interactive Streamlit frontend, and a robust architecture for integrating with external services like Google Drive, Dropbox, and more.

Version 3.0 represents a major architectural upgrade, focusing on production-readiness, enterprise governance, advanced AI capabilities, and a flexible framework for data source integration.

## Key Features

*   **Enterprise Governance & Security:**
    *   **Role-Based Access Control (RBAC):** A clear separation between `user` and `admin` roles, ensuring users can only access their own data.
    *   **Full User Management UI:** A dedicated admin interface for inviting, deleting, and managing user roles.
    *   **Detailed Audit Logs:** A comprehensive, viewable log of all significant actions taken within the application for security and compliance.
*   **Advanced AI & RAG Pipeline:**
    *   **Hybrid Search:** Combines traditional keyword search with vector search to improve retrieval accuracy.
    *   **Re-ranking Model:** A secondary AI model re-ranks search results for relevance before they are sent to the LLM, increasing answer quality.
    *   **Conversational Memory:** The system remembers the context of previous questions, allowing for natural, multi-turn conversations.
*   **Flexible Data Source Integration:**
    *   **Two Modes of Operation:**
        1.  **Managed Storage:** Upload files directly or ingest them from connected services into the application's secure storage, with a universal, configurable storage quota for all users.
        2.  **Read-on-the-fly:** Query files directly from connected services like Google Drive without ever storing them on the application's servers.
    *   **Multiple Connectors:** Built-in, production-ready integrations for Google Drive, Dropbox, Microsoft OneDrive, and Atlassian Confluence.
*   **Enhanced User Experience:**
    *   **Asynchronous Processing:** Long-running tasks like file uploads and ingestions are handled in the background, with in-app notifications upon completion.
    *   **Saved Data Sources:** A secure system for users to save and manage their connections to external services.

## Technology Stack

*   **Backend:** FastAPI
*   **Frontend:** Streamlit
*   **Databases:** PostgreSQL, ChromaDB
*   **Core Libraries:** Langchain, SQLAlchemy, Pydantic, Sentence-Transformers, Cryptography
*   **Key Integrations:** Google API, Dropbox API, Microsoft Graph API, Atlassian API

## Project Structure

The V3.0 codebase has been professionally restructured for scalability and maintainability, with a clear separation of concerns in a top-level `src` directory.

---
(Setup and running instructions follow, with added details on configuring all API keys and the new `FERNET_KEY` in the `.env` file.)
