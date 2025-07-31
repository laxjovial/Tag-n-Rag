from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

import uuid
from datetime import timedelta
from .. import schemas
from ..database import get_db
from ..models import Document, User, Setting, Category
from ..rag import RAGSystem
from .auth import get_current_active_user
from ..utils import read_file_content
from ..services.storage import CloudStorageService

router = APIRouter()

# Create shared instances of services
rag_system = RAGSystem()
storage_service = CloudStorageService()

from typing import List

@router.post("/upload", response_model=List[schemas.DocumentOut])
def upload_documents(
    files: List[UploadFile] = File(...),
    expires_at: Optional[str] = Form(None),
    category_ids: Optional[List[int]] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    uploaded_docs = []

    # Get default expiration from settings
    default_expiration_days = None
    setting = db.query(Setting).filter(Setting.key == "default_expiration_days").first()
    if setting and setting.value.isdigit():
        default_expiration_days = int(setting.value)

    # Fetch categories if provided
    categories = []
    if category_ids:
        categories = db.query(Category).filter(Category.id.in_(category_ids)).all()

    for file in files:
        try:
            document_text = read_file_content(file)
        except ValueError as e:
            print(f"Skipping unsupported file '{file.filename}': {e}")
            continue

        unique_filename = f"{uuid.uuid4()}_{file.filename}"

        try:
            storage_service.upload(file=file, destination_filename=unique_filename)
        except Exception as e:
            print(f"Failed to upload '{file.filename}', skipping this file. Error: {e}")
            continue

        db_document = Document(
            filename=unique_filename,
            original_filename=file.filename,
            owner_id=current_user.id,
            categories=categories, # Assign categories
        )

        if expires_at:
            db_document.expires_at = datetime.fromisoformat(expires_at)
        elif default_expiration_days is not None:
            db_document.expires_at = datetime.utcnow() + timedelta(days=default_expiration_days)

        db.add(db_document)
        db.commit()
        db.refresh(db_document)

        # 4. Process the document with the RAG system
        rag_system.process_document(document_id=db_document.id, document_text=document_text)

        uploaded_docs.append(db_document)

    if not uploaded_docs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid files were uploaded."
        )

    return uploaded_docs


@router.get("/", response_model=List[schemas.DocumentOut])
def list_user_documents(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = db.query(Document).filter(Document.owner_id == current_user.id)
    if search:
        query = query.filter(Document.filename.ilike(f"%{search}%"))
    return query.all()


@router.get("/{document_id}", response_model=schemas.DocumentOut)
def get_document_details(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    document = db.query(Document).filter(
        Document.id == document_id, Document.owner_id == current_user.id
    ).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    document = db.query(Document).filter(
        Document.id == document_id, Document.owner_id == current_user.id
    ).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # 1. Delete from RAG system (vector store)
    rag_system.delete_document(document_id=document.id)

    # 2. Delete from database
    db.delete(document)
    db.commit()

    return None
