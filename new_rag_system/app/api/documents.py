# In api/documents.py
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError # Import for handling database integrity errors

import uuid
import io
from .. import schemas
from ..database import get_db
from ..models import Document, User, Setting, Category, document_category_association # Import document_category_association
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
    expires_at: Optional[str] = Form(None), # Expecting ISO format string
    category_ids: Optional[List[int]] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Uploads one or more documents, stores them, and creates database entries.
    Optionally assigns categories and an expiration date.
    """
    uploaded_docs = []
    for file in files:
        # Generate a unique filename for storage
        file_extension = file.filename.split(".")[-1] if "." in file.filename else "txt"
        unique_filename = f"{uuid.uuid4()}.{file_extension}"

        # Read file content
        content = read_file_content(file) # Assuming read_file_content handles different types

        # Upload to storage service
        try:
            storage_service.upload(unique_filename, content.encode('utf-8'))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to upload file to storage: {e}")

        # Convert expires_at string to datetime object if provided
        expires_at_dt = None
        if expires_at:
            try:
                expires_at_dt = datetime.fromisoformat(expires_at)
            except ValueError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid expiration date format. Use ISO 8601.")

        # Create document entry in database
        db_document = Document(
            filename=unique_filename,
            original_filename=file.filename,
            version=1, # Initial version
            owner_id=current_user.id,
            created_at=datetime.utcnow(),
            expires_at=expires_at_dt,
            # content is stored in the cloud, not directly in this Document model
        )
        db.add(db_document)
        db.flush() # Flush to get the document ID before adding categories

        # Associate with categories
        if category_ids:
            for cat_id in category_ids:
                category = db.query(Category).filter(Category.id == cat_id).first()
                if not category:
                    # Optionally, you could choose to ignore invalid categories or log a warning
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Category with ID {cat_id} not found.")
                db_document.categories.append(category)

        try:
            db.commit()
            db.refresh(db_document)
            uploaded_docs.append(db_document)
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database integrity error: {e}")
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save document to database: {e}")

    return uploaded_docs

@router.get("/", response_model=List[schemas.DocumentOut])
def list_user_documents(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Lists all documents owned by the current user, with optional search filtering.
    """
    query = db.query(Document).filter(Document.owner_id == current_user.id)

    if search:
        query = query.filter(Document.original_filename.ilike(f"%{search}%"))

    documents = query.all()
    return documents

@router.get("/{document_id}", response_model=schemas.DocumentOut)
def get_document_details(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieves details for a specific document owned by the current user.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found or not owned by user")
    return document

@router.get("/{document_id}/content")
def get_document_content(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieves the raw content of a specific document owned by the current user.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found or not owned by user")

    try:
        content_bytes = storage_service.download(document.filename)
        return StreamingResponse(io.BytesIO(content_bytes), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve document content: {e}")

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Deletes a document from storage and its database entry.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found or not owned by user")

    try:
        # Delete from cloud storage first
        storage_service.delete(document.filename)
    except Exception as e:
        # Log the error but don't prevent DB deletion if storage fails
        print(f"Warning: Failed to delete file from storage: {e}")

    # Delete from database
    db.delete(document)
    db.commit()
    return None # 204 No Content response

@router.put("/{document_id}", response_model=schemas.DocumentOut)
def update_document_content(
    document_id: int,
    update_data: schemas.DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Updates the content of an existing document. This creates a new version.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found or not owned by user")

    # Generate a new unique filename for the updated version
    file_extension = document.filename.split(".")[-1]
    new_unique_filename = f"{uuid.uuid4()}.{file_extension}"

    try:
        # Upload new content to storage
        storage_service.upload(new_unique_filename, update_data.content.encode('utf-8'))

        # Update document entry in database
        document.filename = new_unique_filename
        document.version += 1
        # You might want to update a 'updated_at' timestamp here if your model has one
        db.commit()
        db.refresh(document)
        return document
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update document content: {e}")

@router.post("/from_text", response_model=schemas.DocumentOut)
def create_document_from_text(
    data: schemas.DocumentCreateFromText,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Creates a new document from plain text content.
    """
    # Generate a unique filename for storage
    unique_filename = f"{uuid.uuid4()}.txt" # Assuming text content, so .txt extension

    # Upload content to storage service
    try:
        storage_service.upload(unique_filename, data.content.encode('utf-8'))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to upload text content to storage: {e}")

    # Convert expires_at string to datetime object if provided
    expires_at_dt = None
    # Assuming schemas.DocumentCreateFromText doesn't have expires_at,
    # but if it did, you'd handle it here.

    # Create document entry in database
    db_document = Document(
        filename=unique_filename,
        original_filename=data.filename, # Use filename from input for original_filename
        version=1,
        owner_id=current_user.id,
        created_at=datetime.utcnow(),
        expires_at=expires_at_dt,
    )
    db.add(db_document)
    db.flush() # Flush to get the document ID before adding categories

    # Associate with categories
    if data.category_ids:
        for cat_id in data.category_ids:
            category = db.query(Category).filter(Category.id == cat_id).first()
            if not category:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Category with ID {cat_id} not found.")
            db_document.categories.append(category)

    try:
        db.commit()
        db.refresh(db_document)
        return db_document
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database integrity error: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save document from text to database: {e}")

@router.get("/{document_id}/export")
def export_document(
    document_id: int,
    format: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Exports a document in a specified format (PDF, DOCX, TXT).
    """
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
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingprocessingml.document"
        filename = f"{document.original_filename}.docx"
    else:
        file_buffer = export_service.to_txt(content)
        media_type = "text/plain"
        filename = f"{document.original_filename}.txt"

    return StreamingResponse(
        io.BytesIO(file_buffer), # Ensure it's a BytesIO object for StreamingResponse
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

