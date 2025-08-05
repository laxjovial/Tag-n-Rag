# User Guide: Advanced RAG System (V3.0)

## 1. Welcome!
Welcome to the Advanced RAG System! This guide will walk you through all the features available to you as a user.

## 2. Core Features
*   **Uploading & Creating Documents:** You can upload files directly or create documents from text. These files are stored in the application's secure storage and count against your storage quota.
*   **Querying:** Ask questions of your uploaded documents, either individually or by category.
*   **History & Export:** View your past queries in the "History" page and export the results.

## 3. Connecting External Services
Navigate to the **Manage Connections** page from the sidebar to connect your external accounts.
*   **Connect:** For each available service (Google Drive, Dropbox, etc.), click "Connect" and follow the authorization prompts from that service.
*   **Manage:** Once connected, you can see your active connections and delete them if you wish.

## 4. Working with Connected Services
Once a service like Google Drive is connected, you have two ways to use your files:

### Mode 1: Upload from Drive
1.  Go to the **Manage Connections** page and select the "Upload from..." tab.
2.  Browse your files and select the ones you wish to import.
3.  Click "Upload". This copies the files to the application's storage, making them permanently available for querying (this uses your storage quota).

### Mode 2: Read-on-the-fly (for Google Drive)
This powerful feature lets you query files directly in your Drive without uploading them.
1.  **Map a Category:** Go to the **Manage Mappings** page and link one of your app categories to a specific Google Drive folder.
2.  **Query:** Go to the **Query** page. Your mapped category will now appear with a cloud icon (☁️). When you query this category, the system will temporarily read the files from your Drive to answer the question.

## 5. Conversational Queries
The Query page now supports multi-turn conversations. After you get an answer, you can ask a follow-up question in the chat input, and the system will remember the context of your previous questions.

## 6. Your Analytics
The **My Analytics** page shows a dashboard of your personal activity, including:
*   **Storage Usage:** A progress bar showing how much of your storage quota you have used for uploaded/ingested files.
*   **Query Usage:** Your total number of queries and other statistics.
