# Recruiter Overview: Advanced RAG System

## Project Summary

This project is a full-stack, enterprise-grade Retrieval-Augmented Generation (RAG) system. It provides a complete solution for organizations to turn their internal documents into a secure, queryable knowledge base. The application features a Python-based backend using FastAPI and an interactive frontend built with Streamlit.

As the sole developer, I was responsible for the entire lifecycle of this project, from conceptualization and architectural design to implementation and documentation.

---

## Key Technical Achievements & Demonstrated Skills

This project showcases a wide range of skills in modern software engineering, AI implementation, and full-stack development.

### 1. Backend Development (Python, FastAPI)

*   **Cloud Service & External API Integration:**
    *   Integrated the application with Google Cloud Storage (GCS) for persistent, scalable document storage.
    *   **Google Drive API (V2.0):** Implemented a secure OAuth 2.0 flow and created a dedicated service to interact with the Google Drive API, enabling features like file browsing, ingestion, and "read-on-the-fly" queries.
*   **Complex Feature Implementation:**
    *   Designed and implemented advanced, user-centric features such as personal document categorization, editable documents, and a full knowledge creation loop (saving/appending queries to documents).
    *   **Storage Quotas (V2.0):** Engineered a universal, environment-configurable storage limit system to manage resources, including all necessary database tracking and backend enforcement logic.
*   **Advanced Database Design:** Designed and implemented a many-to-many relationship in SQLAlchemy to support document categorization.
*   **Third-Party Library Integration:** Researched and integrated libraries like `reportlab` to build a robust document export service (PDF, DOCX, TXT).
*   **API Design:** Designed and built a comprehensive RESTful API to handle user authentication, document management, querying, and admin functions.
*   **Authentication & Security (JWT):** Designed and implemented a secure, stateless user authentication and authorization system from scratch using JSON Web Tokens (JWT). This demonstrates a strong understanding of modern security practices, including password hashing (`passlib`) and token lifecycle management.
*   **Asynchronous Processing:** Developed a background task manager within FastAPI to handle long-running processes like document expiration and user notifications.

### 2. AI and Machine Learning (Langchain, ChromaDB)

*   **RAG Pipeline Implementation:** Engineered the core AI functionality, including document loading (PDF, DOCX, TXT), text splitting, vector embedding, and retrieval.
*   **Vector Database Management:** Integrated ChromaDB as the vector store for efficient similarity searching.
*   **Flexible Generation:** Designed a highly flexible generation module that can seamlessly switch between different Large Language Models (e.g., from OpenAI, Anthropic) and external, third-party APIs, all configured via a simple YAML file. This demonstrates an understanding of modular and extensible AI systems.

### 3. Frontend Development (Python, Streamlit)

*   **Interactive UI/UX:** Built a user-friendly, multi-page web application using Streamlit, providing a seamless experience for users and administrators.
*   **State Management:** Effectively managed user session data, including authentication state and API tokens, within the Streamlit framework.
*   **API Consumption:** Connected the frontend to the FastAPI backend, handling API requests and responses for a dynamic user experience.

### 4. Software Architecture & Design

*   **System Design:** Architected a scalable, decoupled system with a clear separation of concerns between the frontend, backend, and data layers.
*   **Database Schema Design:** Designed a normalized relational database schema in PostgreSQL to efficiently store and manage users, document metadata, versioning, and query logs.
*   **Configuration Management:** Implemented a robust configuration system using environment variables and YAML files to manage sensitive keys and application settings, a best practice for deployable applications.

---

## Technology Stack Summary

*   **Languages:** Python
*   **Backend:** FastAPI
*   **Frontend:** Streamlit
*   **AI/ML:** Langchain, Sentence-Transformers
*   **Databases:** PostgreSQL (for structured data), ChromaDB (for vector data)
*   **Libraries:** SQLAlchemy, Pydantic, Passlib, PyYAML
*   **Tools:** Docker, Git
