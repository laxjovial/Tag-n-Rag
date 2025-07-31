# Admin Guide: Advanced RAG System

## 1. Introduction

This guide is for system administrators. It covers all the features available in the admin dashboard, which allow you to manage users, system configurations, and monitor activity across the platform.

---

## 2. Accessing the Admin Dashboard

To access the admin dashboard, you must be logged in with an account that has the "admin" role.

1.  Log in to the application with your admin credentials.
2.  In the main navigation sidebar, you will see an "Admin" page. Click on it to open the admin dashboard.

---

## 3. User Management

The user management section gives you full control over the user accounts on the system.

*   **View All Users:** The main view of this section displays a table of all registered users, showing their username, role, and registration date.
*   **Create a New User:**
    1.  Click the "Create User" button.
    2.  Fill in the username, a temporary password, and select a role (`user` or `admin`).
    3.  The new user will be created, and they can log in with the temporary password.
*   **Edit a User's Role:**
    1.  Find the user in the user list.
    2.  Click the "Edit" button next to their name.
    3.  You can change their role from `user` to `admin` (or vice versa). This change takes effect immediately.
*   **Delete a User:**
    1.  Find the user in the list.
    2.  Click the "Delete" button.
    3.  A confirmation dialog will appear. Please be aware that deleting a user is a permanent action and will also remove their associated data.

---

## 4. LLM and API Configuration

This section allows you to control which Language Models (LLMs) and external APIs are available for users in the "Query" page.

*   **View Configurations:** The page displays a list of all currently configured LLM and API providers.
*   **Add a New Configuration:**
    1.  Click "Add New Configuration".
    2.  Choose the type: `LLM` or `API`.
    3.  Fill in the required fields:
        *   **Name:** A user-friendly name that will appear in the model selection dropdown (e.g., "OpenAI GPT-4 Turbo").
        *   **Model / Endpoint:** The specific model name (e.g., `gpt-4-1106-preview`) or the full URL of the external API.
        *   **API Key Environment Variable:** The name of the environment variable where the API key is stored on the server (e.g., `OPENAI_API_KEY`). **Note:** You do not enter the key itself here, only the name of the variable.
    4.  Click "Save". The new configuration will be immediately available to users.
*   **Edit a Configuration:** Click the "Edit" button next to any configuration to modify its details.
*   **Set as Default:** Each list (LLMs and APIs) can have one default. This is the model that will be pre-selected for users on the Query page. To set a default, click the "Set as Default" button next to the desired configuration.

---

## 5. Global Query History

The global query history page provides a comprehensive log of all queries made by all users across the system. This is useful for monitoring usage, understanding user behavior, and troubleshooting issues.

*   **View History:** The page displays a searchable and filterable table of all queries.
*   **Search and Filter:** You can filter the history log by:
    *   Username
    *   Date range
    *   Keywords in the query text

This allows you to quickly find specific information about system usage.

---

## 6. Category Management

As an admin, you can view and delete any categories created by users. This is useful for maintaining a clean and organized set of categories.

*   **View Categories:** A list of all categories is available in the "Categories" section of the admin dashboard.
*   **Delete a Category:** You can delete a category by clicking the "Delete" button next to it. This will not delete the documents within the category, only the category itself.

## 7. System Settings

You can configure system-wide settings from the "Settings" tab.

*   **Default Document Expiration:** Set a default number of days after which newly uploaded documents will expire.
*   **Theme Settings:** Set a default theme for all new users.

---

## 8. Usage Analytics

The "Analytics" tab provides a dashboard with visualizations of system usage, such as the number of queries performed per day. This is useful for monitoring the system's activity and understanding user engagement.
