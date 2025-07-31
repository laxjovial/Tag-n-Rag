# Backend Application

This directory contains all the backend source code for the Advanced RAG System. It is a FastAPI application.

## Directory Structure

-   `api/`: Contains the API routers, which define the application's endpoints.
-   `models/`: Contains the SQLAlchemy database models.
-   `services/`: Contains the business logic and services, such as the `RAGSystem`, `CloudStorageService`, and background tasks.
-   `database.py`: Sets up the database connection and session management.
-   `main.py`: The main entry point for the FastAPI application.
-   `schemas.py`: Contains the Pydantic schemas for data validation.
-   `utils.py`: Contains utility functions.
