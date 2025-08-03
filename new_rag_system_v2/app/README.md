# Backend Application

This directory contains all the backend source code for the Advanced RAG System. It is a FastAPI application.

## Directory Structure

-   `api/`: Contains the API routers, which define the application's endpoints (e.g., for auth, documents, queries).
-   `models/`: Contains the SQLAlchemy database models (e.g., User, Document, Category).
-   `services/`: Contains the core business logic and services, such as the `RAGSystem`, `CloudStorageService`, `ExportService`, and background tasks.
-   `database.py`: Sets up the database connection (engine, session) and the declarative base for models.
-   `main.py`: The main entry point for the FastAPI application.
-   `schemas.py`: Contains the Pydantic schemas for data validation.
-   `utils.py`: Contains utility functions.
