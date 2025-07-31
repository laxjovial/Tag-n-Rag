# API Routers

This directory contains the API routers for the FastAPI application. Each file defines a set of related endpoints.

## Files

-   `auth.py`: Handles user registration and JWT-based login.
-   `categories.py`: Handles CRUD operations for document categories.
-   `documents.py`: Handles document uploading, listing, updating, and deletion.
-   `notifications.py`: Handles fetching and managing user notifications.
-   `query.py`: Handles the main RAG query and export functionality.
-   `admin.py`: Contains all endpoints restricted to admin users, such as analytics and system settings.
