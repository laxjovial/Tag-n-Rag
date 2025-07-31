# Services

This directory contains the core business logic of the application, encapsulated in services.

## Files

-   `rag.py`: Contains the `RAGSystem` class, which is the heart of the retrieval and generation pipeline.
-   `storage.py`: Contains the `CloudStorageService` for interacting with Google Cloud Storage.
-   `expiration.py`: Contains the background services for handling document expiration and sending user notifications.
-   `export.py`: Contains the `ExportService` for generating different file formats (PDF, DOCX, TXT) from text content.
