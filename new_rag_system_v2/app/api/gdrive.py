import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import schemas
from ..database import get_db
from ..models import User, Document
from .auth import get_current_active_user
from ..services.google_drive import GoogleDriveService
from ..services.storage import CloudStorageService

router = APIRouter()
storage_service = CloudStorageService()

# --- Storage Limit Configuration ---
USER_STORAGE_LIMIT_MB = int(os.environ.get("USER_STORAGE_LIMIT_MB", 1024))
USER_STORAGE_LIMIT_BYTES = USER_STORAGE_LIMIT_MB * 1024 * 1024

@router.get("/files")
def list_drive_files(
    folder_id: Optional[str] = 'root',
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not current_user.google_credentials:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google account not connected.")
    try:
        gdrive_service = GoogleDriveService(current_user.google_credentials)
        files = gdrive_service.list_files(folder_id=folder_id)
        return files
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to list Google Drive files: {e}")

@router.post("/ingest", response_model=List[schemas.DocumentOut])
def ingest_from_google_drive(
    ingest_request: schemas.GoogleDriveIngestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not current_user.google_credentials:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google account not connected.")

    gdrive_service = GoogleDriveService(current_user.google_credentials)
    ingested_docs = []

    # First, check total size if possible. This is complex as we need to get metadata for all files.
    # For simplicity, we'll check one by one. A more advanced implementation would pre-fetch sizes.

    for file_id in ingest_request.file_ids:
        try:
            # A proper implementation would get file metadata (like size and name) first
            # gdrive_service.get_file_metadata(file_id)
            # For now, we download and then check size.

            file_content_buffer = gdrive_service.download_file(file_id)
            file_size = len(file_content_buffer.getvalue())

            if current_user.storage_used + file_size > USER_STORAGE_LIMIT_BYTES:
                # We stop at the first file that would exceed the limit.
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Ingesting this file would exceed your storage limit of {USER_STORAGE_LIMIT_MB} MB."
                )

            unique_filename = f"{uuid.uuid4()}.gdoc"
            storage_service.upload(unique_filename, file_content_buffer.getvalue())

            db_document = Document(
                filename=unique_filename,
                original_filename=f"gdrive_{file_id}", # Placeholder
                version=1,
                owner_id=current_user.id,
                created_at=datetime.utcnow(),
                size=file_size
            )

            db.add(db_document)
            current_user.storage_used += file_size

            db.commit()
            db.refresh(db_document)
            ingested_docs.append(db_document)

        except HTTPException as http_exc:
            # Re-raise HTTP exceptions to be sent to the client
            raise http_exc
        except Exception as e:
            db.rollback()
            print(f"Failed to ingest file {file_id}: {e}")

    return ingested_docs
