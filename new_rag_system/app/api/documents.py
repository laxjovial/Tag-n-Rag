import os
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import uuid
import io
from .. import schemas
from ..database import get_db
from ..models import Document, User, Setting, Category, document_category_association, QueryLog
from ..rag import RAGSystem
from .auth import get_current_active_user
from ..utils import read_file_content
from ..services.storage import CloudStorageService
from ..services.export import ExportService

router = APIRouter()

rag_system = RAGSystem()
storage_service = CloudStorageService()
export_service = ExportService()

# --- Storage Limit Configuration ---
USER_STORAGE_LIMIT_MB = int(os.environ.get("USER_STORAGE_LIMIT_MB", 1024))
USER_STORAGE_LIMIT_BYTES = USER_STORAGE_LIMIT_MB * 1024 * 1024

@router.post("/upload", response_model=List[schemas.DocumentOut])
def upload_documents(
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

    uploaded_docs = []
    for file in files:
        file_content_bytes = file.file.read()
        file.file.seek(0) # Reset file pointer
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

# (The rest of the file remains the same, so I'm omitting it for brevity)
# ...
# I will now update the delete_document function in a separate step.
# ...
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
    Deletes a document from storage, its database entry, and updates user storage usage.
    """
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
        current_user.storage_used = 0 # Prevent negative storage

    db.commit()
    return None

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
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
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

@router.post("/{document_id}/append", response_model=schemas.DocumentOut)
def append_to_document(
    document_id: int,
    append_data: schemas.DocumentAppend,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Appends a formatted query result to an existing document.
    """
    # 1. Verify ownership of the target document
    document = db.query(Document).filter(Document.id == document_id, Document.owner_id == current_user.id).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # 2. Verify ownership of the source query
    query_log = db.query(QueryLog).filter(QueryLog.id == append_data.query_id, QueryLog.user_id == current_user.id).first()
    if not query_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Query log not found")

    # 3. Download the existing document content
    try:
        original_content = storage_service.download(document.filename).decode('utf-8')
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not retrieve original document: {e}")

    # 4. Format the new content
    query_content = f"Question: {query_log.query_text}\n\nAnswer: {query_log.answer_text}"
    formatted_append_text = ""
    if append_data.formatting_method == 'simple':
        formatted_append_text = f"\n\n---\n\n{query_content}"
    elif append_data.formatting_method == 'informative':
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        formatted_append_text = f"\n\n--- Appended on {timestamp} ---\n\n{query_content}"
    elif append_data.formatting_method == 'structured':
        timestamp = datetime.utcnow().strftime('%Y-%m-%d')
        formatted_append_text = f"\n\n## Query Result\n**Date:** {timestamp}\n**Question:** {query_log.query_text}\n\n**Answer:**\n{query_log.answer_text}"
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid formatting method")

    # 5. Combine and upload the new content
    new_content = original_content + formatted_append_text
    new_unique_filename = f"{uuid.uuid4()}.{document.filename.split('.')[-1]}"

    try:
        storage_service.upload(new_unique_filename, new_content.encode('utf-8'))

        # 6. Update document metadata (new version, new filename)
        document.filename = new_unique_filename
        document.version += 1
        db.commit()
        db.refresh(document)

        return document
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to append to document: {e}")
