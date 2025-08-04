# Services

This directory contains the core business logic of the application, encapsulated in services.

## Files

-   `rag.py`: Contains the `RAGSystem` class, which is the heart of the retrieval and generation pipeline. It now includes a `query_on_the_fly` method for handling non-ingested content.
-   `storage.py`: Contains the `CloudStorageService` for interacting with the application's managed GCS bucket.
-   `google_drive.py`: (V2.0) Contains the `GoogleDriveService` for interacting with the Google Drive API on behalf of the user.
-   `expiration.py`: Contains the background services for handling document expiration and sending user notifications.
-   `export.py`: Contains the `ExportService` for generating different file formats (PDF, DOCX, TXT) from text content.
