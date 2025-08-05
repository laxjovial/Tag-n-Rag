import os
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import uuid
import io
from src.backend.data import schemas
from src.backend.data.database import get_db, SessionLocal
from src.backend.data.models import Document, User, Setting, Category, Notification, QueryLog
from src.backend.core.rag_system import RAGSystem
from src.backend.api.auth import get_current_active_user
from src.backend.core.audit import create_audit_log
from src.frontend.utils import read_file_content
from src.backend.core.services.storage import CloudStorageService
from src.backend.core.services.export import ExportService

router = APIRouter()

rag_system = RAGSystem()
storage_service = CloudStorageService()
export_service = ExportService()

# --- Storage Limit Configuration ---
USER_STORAGE_LIMIT_MB = int(os.environ.get("USER_STORAGE_LIMIT_MB", 1024))
USER_STORAGE_LIMIT_BYTES = USER_STORAGE_LIMIT_MB * 1024 * 1024

def process_and_save_file(file_content_bytes: bytes, original_filename: str, user_id: int, expires_at_iso: Optional[str], category_ids: Optional[List[int]]):
    """
    Background task to process a single uploaded file.
    """
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            # Handle case where user is deleted before task runs
            return

        file_size = len(file_content_bytes)
        unique_filename = f"{uuid.uuid4()}.{original_filename.split('.')[-1]}"

        storage_service.upload(unique_filename, file_content_bytes)

        expires_at_dt = datetime.fromisoformat(expires_at_iso) if expires_at_iso else None

        db_document = Document(
            filename=unique_filename,
            original_filename=original_filename,
            version=1,
            owner_id=user_id,
            created_at=datetime.utcnow(),
            expires_at=expires_at_dt,
            size=file_size
        )

        if category_ids:
            categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
            db_document.categories.extend(categories)

        db.add(db_document)
        user.storage_used += file_size

        notification = Notification(user_id=user.id, message=f"Successfully processed and saved '{original_filename}'.")
        db.add(notification)

        db.commit()
        db.refresh(db_document)

        create_audit_log(db, user, "document_upload_success", {"document_id": db_document.id, "filename": original_filename})

        # After saving, process for RAG
        # This is a long-running task that should also be backgrounded in a real production system
        # For now, we do it synchronously within this background task.
        rag_system.process_document(document_id=db_document.id, document_text=file_content_bytes.decode('utf-8', errors='ignore'))

    except Exception as e:
        # Log the error and create a failure notification
        print(f"Failed to process file {original_filename}: {e}")
        notification = Notification(user_id=user_id, message=f"Failed to process '{original_filename}'. Please try again.")
        db.add(notification)
        create_audit_log(db, user, "document_upload_failed", {"filename": original_filename, "error": str(e)})
        db.commit()
    finally:
        db.close()

@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
def upload_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    expires_at: Optional[str] = Form(None),
    category_ids: Optional[List[int]] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    total_upload_size = sum(file.size for file in files)
    if current_user.storage_used + total_upload_size > USER_STORAGE_LIMIT_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Upload would exceed your storage limit of {USER_STORAGE_LIMIT_MB} MB."
        )

    for file in files:
        # Read file content into memory. For very large files, this could be an issue.
        # A more robust solution would stream the file to a temporary location.
        file_content_bytes = file.file.read()
        background_tasks.add_task(
            process_and_save_file,
            file_content_bytes,
            file.filename,
            current_user.id,
            expires_at,
            category_ids
        )

    return {"message": f"File upload started for {len(files)} file(s). You will be notified upon completion."}

# ... (rest of the file)
