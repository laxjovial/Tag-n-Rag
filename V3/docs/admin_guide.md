# Admin Guide: Advanced RAG System (V3.0)

## 1. Introduction
This guide is for system administrators. It covers all the features available in the admin dashboard.

## 2. Admin Dashboard Tabs
The admin dashboard is organized into multiple tabs for easy management.

### 2.1. User Management
This tab is now a fully interactive interface for managing users.
*   **Invite User:** Use the form to invite a new user by username and email. They will be created with the 'user' role.
*   **Manage Existing Users:** For each user, you can:
    *   View their current storage usage.
    *   Change their role between 'user' and 'admin'.
    *   Delete the user and all their associated data from the system.

### 2.2. Audit Log
This tab provides a comprehensive, paginated view of all significant actions taken within the application. You can see who took what action and when, which is crucial for security and compliance.

### 2.3. Other Tabs
*   **LLM/API Configs:** A read-only view of the system's configured LLM providers.
*   **Global History:** A read-only view of all queries made by all users.
*   **System Analytics:** A dashboard for system-wide usage metrics.
