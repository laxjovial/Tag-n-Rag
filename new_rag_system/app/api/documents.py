from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

import uuid
import io
from .. import schemas
from ..database import get_db
from ..models import Document, User, Setting, Category
from ..rag import RAGSystem
from .auth import get_current_active_user
from ..utils import read_file_content
from ..services.storage import CloudStorageService
from ..services.export import ExportService

router = APIRouter()

rag_system = RAGSystem()
storage_service = CloudStorageService()
export_service = ExportService()

@router.post("/upload", response_model=List[schemas.DocumentOut])
def upload_documents(
    files: List[UploadFile] = File(...),
    expires_at: Optional[str] = Form(None),
    category_ids: Optional[List[int]] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # ... (existing upload logic)
    pass

@router.get("/", response_model=List[schemas.DocumentOut])
def list_user_documents(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # ... (existing list logic)
    pass

@router.get("/{document_id}", response_model=schemas.DocumentOut)
def get_document_details(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # ... (existing details logic)
    pass

@router.get("/{document_id}/content")
def get_document_content(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # ... (existing content logic)
    pass

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # ... (existing delete logic)
    pass

@router.put("/{document_id}", response_model=schemas.DocumentOut)
def update_document_content(
    document_id: int,
    update_data: schemas.DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # ... (existing update logic)
    pass

@router.post("/from_text", response_model=schemas.DocumentOut)
def create_document_from_text(
    data: schemas.DocumentCreateFromText,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # ... (existing create from text logic)
    pass

@router.get("/{document_id}/export")
def export_document(
    document_id: int,
    format: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    document = db.query(Document).filter(Document.id == document_id, Document.owner_id == current_user.id).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    content_bytes = storage_service.download(document.filename)
    content = content_bytes.decode('utf-8')

    if format == "pdf":
        file_buffer = export_service.to_pdf(content)
        media_type = "application/pdf"
        filename = f"{document.original_filename}.pdf"
    elif format == "docx":
        file_buffer = export_service.to_docx(content)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"{document.original_filename}.docx"
    else:
        file_buffer = export_service.to_txt(content)
        media_type = "text/plain"
        filename = f"{document.original_filename}.txt"

    return StreamingResponse(
        file_buffer,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
