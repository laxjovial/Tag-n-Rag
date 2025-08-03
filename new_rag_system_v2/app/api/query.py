from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import io

from .. import schemas
from ..database import get_db
from ..models import QueryLog, User, Document, Category, LLMConfig, GoogleDriveFolderMapping
from ..services.export import ExportService
from ..services.storage import CloudStorageService
from ..services.google_drive import GoogleDriveService
from ..rag import RAGSystem
from .auth import get_current_active_user

router = APIRouter()
rag_system = RAGSystem()
export_service = ExportService()
storage_service = CloudStorageService()

@router.post("/", response_model=schemas.QueryOutput)
def query_documents(
    query_input: schemas.QueryInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Processes a user query against selected documents or categories using an LLM.
    Handles both uploaded documents and read-on-the-fly from Google Drive.
    """
    llm_config_db = db.query(LLMConfig).filter(LLMConfig.id == query_input.llm_config_id).first() or \
                    db.query(LLMConfig).filter(LLMConfig.is_default == True).first()
    if not llm_config_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No LLM configuration found.")

    llm_config_for_rag = { "name": llm_config_db.name, "model_name": llm_config_db.model_name, "api_key_env": llm_config_db.api_key_env }

    answer = ""
    queried_doc_ids = []

    if query_input.category_id:
        category = db.query(Category).filter(Category.id == query_input.category_id, Category.user_id == current_user.id).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        # Read-on-the-fly logic
        if category.gdrive_mapping:
            if not current_user.google_credentials:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google account not connected.")

            gdrive_service = GoogleDriveService(current_user.google_credentials)
            drive_files = gdrive_service.list_files(folder_id=category.gdrive_mapping.folder_id)

            combined_content = ""
            for file in drive_files:
                if file['mimeType'] != 'application/vnd.google-apps.folder':
                    content_buffer = gdrive_service.download_file(file['id'])
                    combined_content += content_buffer.getvalue().decode('utf-8') + "\n\n"

            if not combined_content:
                answer = "No queryable files found in the mapped Google Drive folder."
            else:
                answer = rag_system.query_on_the_fly(question=query_input.question, content=combined_content, llm_config=llm_config_for_rag)

        # Standard logic for uploaded documents in a category
        else:
            doc_ids_to_query = [doc.id for doc in category.documents]
            if not doc_ids_to_query:
                 answer = "No documents found in this category."
            else:
                answer = rag_system.query(question=query_input.question, document_ids=doc_ids_to_query, llm_config=llm_config_for_rag)
                queried_doc_ids = doc_ids_to_query

    elif query_input.document_ids:
        # Validate ownership of all requested documents
        valid_docs = db.query(Document).filter(Document.id.in_(query_input.document_ids), Document.owner_id == current_user.id).all()
        if len(valid_docs) != len(query_input.document_ids):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to one or more documents.")

        doc_ids_to_query = [doc.id for doc in valid_docs]
        answer = rag_system.query(question=query_input.question, document_ids=doc_ids_to_query, llm_config=llm_config_for_rag)
        queried_doc_ids = doc_ids_to_query

    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Either category_id or document_ids must be provided.")

    # Log the query
    db_query_log = QueryLog(user_id=current_user.id, query_text=query_input.question, answer_text=answer, queried_documents={"ids": queried_doc_ids})
    db.add(db_query_log)
    db.commit()
    db.refresh(db_query_log)

    return schemas.QueryOutput(answer=answer, query_id=db_query_log.id)

# (The rest of the file remains the same)
# ...
@router.post("/{query_id}/save_as_document", response_model=schemas.DocumentOut)
def save_query_as_document(
    query_id: int,
    new_filename: str = Form(...), # Ensure new_filename is required
    category_ids: Optional[List[int]] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Saves a previous query's question and answer as a new document.
    """
    query_log = db.query(QueryLog).filter(QueryLog.id == query_id, QueryLog.user_id == current_user.id).first()
    if not query_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Query not found or not owned by user")

    content = f"Question: {query_log.query_text}\n\nAnswer: {query_log.answer_text}"
    file_buffer = export_service.to_txt(content) # Get the BytesIO object

    unique_filename = f"{uuid.uuid4()}_{new_filename}.txt" # Ensure unique filename with extension

    # storage_service.upload expects file-like object and destination_filename
    storage_service.upload(file_buffer.getvalue(), unique_filename) # Pass bytes directly if upload expects that

    categories = []
    if category_ids:
        # Fetch categories to link them
        categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
        # Ensure categories exist
        if len(categories) != len(category_ids):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more specified categories not found.")


    db_document = Document(
        filename=unique_filename,
        original_filename=new_filename,
        owner_id=current_user.id,
        created_at=datetime.utcnow(), # Add created_at
        categories=categories,
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    # Assuming rag_system.process_document needs to be called for new documents
    # This might involve embedding the document content for future queries
    rag_system.process_document(document_id=db_document.id, document_text=content)
    return db_document

@router.get("/{query_id}/export")
def export_query_result(
    query_id: int,
    format: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Exports a query result (question and answer) in a specified format.
    """
    query_log = db.query(QueryLog).filter(QueryLog.id == query_id, QueryLog.user_id == current_user.id).first()
    if not query_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Query not found or not owned by user")

    content = f"Question: {query_log.query_text}\n\nAnswer: {query_log.answer_text}"

    if format == "pdf":
        file_buffer = export_service.to_pdf(content)
        media_type = "application/pdf"
        filename = f"query_{query_id}.pdf"
    elif format == "docx":
        file_buffer = export_service.to_docx(content)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"query_{query_id}.docx"
    else:
        file_buffer = export_service.to_txt(content)
        media_type = "text/plain"
        filename = f"query_{query_id}.txt"

    return StreamingResponse(
        io.BytesIO(file_buffer.getvalue()), # Ensure it's a BytesIO object with content for StreamingResponse
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
