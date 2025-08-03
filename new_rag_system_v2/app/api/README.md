# API Routers

This directory contains the API routers for the FastAPI application. Each file defines a set of related endpoints.

## Files

-   `auth.py`: Handles user registration and JWT-based login.
-   `categories.py`: Handles CRUD operations for document categories.
-   `documents.py`: Handles document uploading (from file and text), listing, updating, deleting, and exporting.
-   `history.py`: Handles fetching user query history.
-   `notifications.py`: Handles fetching and managing user notifications.
-   `query.py`: Handles the main RAG query, saving query results, and exporting query results.
-   `user.py`: Handles user profile updates (e.g., theme).
-   `admin.py`: Contains all endpoints restricted to admin users, such as analytics and system settings.
