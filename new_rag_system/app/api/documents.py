from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db, Document, User
from ..rag import RAGSystem
from .auth import get_current_active_user
from ..utils import read_file_content

router = APIRouter()

# Create a single, shared instance of the RAGSystem
# In a larger application, you might manage this with a dependency injection system
rag_system = RAGSystem()

@router.post("/upload", response_model=schemas.DocumentOut)
def upload_document(
    file: UploadFile = File(...),
    expires_at: Optional[str] = Form(None),
    parent_document_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        # 1. Read file content
        document_text = read_file_content(file)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # 2. Save document metadata to the database
    db_document = Document(
        filename=file.filename,
        owner_id=current_user.id,
        parent_document_id=parent_document_id,
    )
    if expires_at:
        db_document.expires_at = datetime.fromisoformat(expires_at)

    # Handle versioning
    if parent_document_id:
        latest_version = db.query(Document).filter(
            Document.parent_document_id == parent_document_id
        ).order_by(Document.version.desc()).first()
        if latest_version:
            db_document.version = latest_version.version + 1

    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    # 3. Process the document with the RAG system
    rag_system.process_document(document_id=db_document.id, document_text=document_text)

    return db_document


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
