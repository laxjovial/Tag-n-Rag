import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from src.backend.data import schemas
from src.backend.data.database import get_db, SessionLocal
from src.backend.data.models import User, Document, Notification
from src.backend.api.auth import get_current_active_user
from src.backend.core.services.google_drive import GoogleDriveService
from src.backend.core.services.storage import CloudStorageService
from src.backend.core.audit import create_audit_log
from src.backend.core.rag_system import RAGSystem

router = APIRouter()
storage_service = CloudStorageService()
rag_system = RAGSystem()

# --- Storage Limit Configuration ---
USER_STORAGE_LIMIT_MB = int(os.environ.get("USER_STORAGE_LIMIT_MB", 1024))
USER_STORAGE_LIMIT_BYTES = USER_STORAGE_LIMIT_MB * 1024 * 1024

def process_gdrive_file(file_id: str, user_id: int):
    """
    Background task to ingest a single file from Google Drive.
    """
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.google_credentials:
            return

        gdrive_service = GoogleDriveService(user.google_credentials)

        # A proper implementation would get metadata first to get name and size
        # For simplicity, we download first.
        file_content_buffer = gdrive_service.download_file(file_id)
        file_content_bytes = file_content_buffer.getvalue()
        file_size = len(file_content_bytes)
        original_filename = f"gdrive_{file_id}.txt" # Placeholder

        if user.storage_used + file_size > USER_STORAGE_LIMIT_BYTES:
            notification = Notification(user_id=user.id, message=f"Failed to import '{original_filename}': Exceeds storage limit.")
            db.add(notification)
            db.commit()
            return

        unique_filename = f"{uuid.uuid4()}.gdoc"
        storage_service.upload(unique_filename, file_content_bytes)

        db_document = Document(
            filename=unique_filename,
            original_filename=original_filename,
            version=1,
            owner_id=user.id,
            created_at=datetime.utcnow(),
            size=file_size
        )
        db.add(db_document)
        user.storage_used += file_size

        notification = Notification(user_id=user.id, message=f"Successfully imported '{original_filename}' from Google Drive.")
        db.add(notification)

        create_audit_log(db, user, "gdrive_ingest_success", {"document_id": db_document.id, "gdrive_file_id": file_id})

        db.commit()

        rag_system.process_document(document_id=db_document.id, document_text=file_content_bytes.decode('utf-8', errors='ignore'))

    except Exception as e:
        print(f"Failed to ingest file {file_id} from GDrive: {e}")
        notification = Notification(user_id=user_id, message=f"Failed to import a file from Google Drive.")
        db.add(notification)
        db.commit()
    finally:
        db.close()

@router.get("/files")
def list_drive_files(
    # ... (same as before)
):
    pass

@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
def ingest_from_google_drive(
    ingest_request: schemas.GoogleDriveIngestRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    if not current_user.google_credentials:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google account not connected.")

    for file_id in ingest_request.file_ids:
        background_tasks.add_task(process_gdrive_file, file_id, current_user.id)

    return {"message": f"Ingestion started for {len(ingest_request.file_ids)} file(s). You will be notified upon completion."}
