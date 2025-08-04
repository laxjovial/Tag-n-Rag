import os
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import uuid
import io
from src.backend.data import schemas
from src.backend.data.database import get_db
from src.backend.data.models import Document, User, Setting, Category, document_category_association, QueryLog
from src.backend.core.rag_system import RAGSystem
from src.backend.api.auth import get_current_active_user
# TODO: This utility is file-processing logic and should be moved to a shared core library
# to avoid a backend dependency on the frontend.
from src.frontend.utils import read_file_content
from src.backend.core.services.storage import CloudStorageService
from src.backend.core.services.export import ExportService

router = APIRouter()

rag_system = RAGSystem()
storage_service = CloudStorageService()
export_service = ExportService()

# (The rest of the file content remains the same as I have already updated it)
# ...
# ... (rest of the file)
@router.post("/upload", response_model=List[schemas.DocumentOut])
def upload_documents(
    files: List[UploadFile] = File(...),
    expires_at: Optional[str] = Form(None),
    category_ids: Optional[List[int]] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    total_upload_size = sum(file.size for file in files)
    if current_user.storage_used + total_upload_size > int(os.environ.get("USER_STORAGE_LIMIT_MB", 1024)) * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Upload would exceed your storage limit."
        )

    uploaded_docs = []
    for file in files:
        file_content_bytes = file.file.read()
        file.file.seek(0)
        file_size = len(file_content_bytes)

        unique_filename = f"{uuid.uuid4()}.{file.filename.split('.')[-1]}"

        try:
            storage_service.upload(unique_filename, file_content_bytes)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to upload file to storage: {e}")

        expires_at_dt = datetime.fromisoformat(expires_at) if expires_at else None

        db_document = Document(
            filename=unique_filename,
            original_filename=file.filename,
            version=1,
            owner_id=current_user.id,
            created_at=datetime.utcnow(),
            expires_at=expires_at_dt,
            size=file_size
        )

        if category_ids:
            categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
            if len(categories) != len(category_ids):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more categories not found.")
            db_document.categories.extend(categories)

        db.add(db_document)
        current_user.storage_used += file_size

        try:
            db.commit()
            db.refresh(db_document)
            uploaded_docs.append(db_document)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save document to database: {e}")

    return uploaded_docs
# ... (rest of the file)
@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found or not owned by user")

    document_size = document.size

    try:
        storage_service.delete(document.filename)
    except Exception as e:
        print(f"Warning: Failed to delete file {document.filename} from storage: {e}")

    db.delete(document)
    current_user.storage_used -= document_size
    if current_user.storage_used < 0:
        current_user.storage_used = 0

    db.commit()
    return None
# ... (rest of the file)
