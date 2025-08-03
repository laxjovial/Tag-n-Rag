# User Guide: Advanced RAG System (Version 2.0)

## 1. Welcome!

Welcome to the Advanced RAG System! This guide will walk you through everything you need to know as a user to make the most out of this powerful tool.

---

## 2. Core Features

(Features such as Login, Upload, Querying uploaded documents, History, etc., are the same as in Version 1.0)

...

---

## 3. Google Drive Integration (New in V2.0)

Version 2.0 allows you to connect your Google Drive account, giving you two powerful ways to work with your documents.

### 3.1. Connecting Your Account
1.  Navigate to the **Connect Data Source** page from the sidebar.
2.  Click the "Connect to Google Drive" button.
3.  You will be redirected to a Google consent screen. Follow the prompts to grant the application read-only access to your Drive files.
4.  Once complete, you will be redirected back to the application. The "Connection Status" tab will now show that you are connected.

### 3.2. Mode 1: Uploading from Google Drive
This mode copies files from your Google Drive into the application's managed storage. This is useful for files you want to query frequently without reconnecting.

1.  Go to the **Connect Data Source** page and select the **Upload from Google Drive** tab.
2.  You will see a browser for your Google Drive files.
3.  Select the checkboxes next to the files you wish to import.
4.  Click "Upload Selected Files". The files will be copied to the application and will now appear in your "View Documents" page like any other uploaded file.

### 3.3. Mode 2: Read-on-the-fly
This mode allows you to query files directly from your Google Drive without ever storing them on our servers.

**Step 1: Map a Category to a Drive Folder**
Before you can query in this mode, you must tell the application which folders to look in.
1.  Navigate to the **Manage Mappings** page.
2.  Create a category in our app if you haven't already (e.g., "Project Reports").
3.  In the "Create New Mapping" form, select your category.
4.  Paste the **Folder ID** from your Google Drive folder's URL.
5.  Give the folder a reference name and click "Create Mapping".

**Step 2: Querying Your Mapped Category**
1.  Go to the **Query** page.
2.  In the sidebar, select the "Category" query target.
3.  In the dropdown, you will see your mapped category, marked with a cloud icon (☁️).
4.  Select this category and ask your question. The system will read the files from the mapped folder in your Drive for this query only.

---

## 4. Analytics and Storage

The **My Analytics** page now shows your personal storage usage for uploaded files, in addition to your query history and statistics.

If you have any questions, don't hesitate to reach out to your system administrator. Happy querying!
