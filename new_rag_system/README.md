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

### Prerequisites

*   Python 3.8+
*   Poetry (or pip) for dependency management
*   Docker and Docker Compose (for running databases)

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd new_rag_system
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    Create a `.env` file in the root directory and add the necessary credentials for your database, LLM providers, and other services. A `env.example` file will be provided to guide you.

4.  **Launch databases:**
    ```bash
    docker-compose up -d
    ```

5.  **Run the backend server:**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```

6.  **Run the Streamlit frontend:**
    Open a new terminal and run:
    ```bash
    streamlit run app.py
    ```
The application will be available at `http://localhost:8501`.
