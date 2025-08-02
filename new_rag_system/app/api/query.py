from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import io

from .. import schemas
from ..database import get_db
from ..models import QueryLog, User, Document, Category, LLMConfig # Ensure LLMConfig is imported
from ..services.export import ExportService
from ..services.storage import CloudStorageService
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
    Logs the query and its answer.
    """
    doc_ids_to_query = []
    if query_input.category_id is not None:
        category = db.query(Category).filter(Category.id == query_input.category_id).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        # Ensure only documents owned by the current user within that category are queried
        doc_ids_to_query = [doc.id for doc in category.documents if doc.owner_id == current_user.id]
    elif query_input.document_ids: # This is a list, so check if it's not empty
        # Validate that the requested documents are owned by the current user
        valid_doc_ids = []
        for doc_id in query_input.document_ids:
            doc = db.query(Document).filter(Document.id == doc_id, Document.owner_id == current_user.id).first()
            if doc:
                valid_doc_ids.append(doc_id)
        doc_ids_to_query = valid_doc_ids
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Either category_id or document_ids must be provided.")

    if not doc_ids_to_query:
        # Return a specific message if no documents are found for the query
        return schemas.QueryOutput(answer="No relevant documents found for your query based on the selected criteria.", query_id=0)

    # Determine LLM configuration
    llm_config_db = None
    if query_input.llm_config_id is not None:
        llm_config_db = db.query(LLMConfig).filter(LLMConfig.id == query_input.llm_config_id).first()
    
    # If no specific LLM config is provided or found, try to get the default
    if not llm_config_db:
        llm_config_db = db.query(LLMConfig).filter(LLMConfig.is_default == True).first()

    if not llm_config_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No LLM configuration found. Please select one or set a default in the Admin panel.")

    # Prepare LLM config dictionary for RAGSystem
    llm_config_for_rag = {
        "type": llm_config_db.name.lower().split(" ")[0],
        "name": llm_config_db.name,
        "model_name": llm_config_db.model_name,
        "api_endpoint": llm_config_db.api_endpoint,
        "api_key_env": llm_config_db.api_key_env,
        "is_api": llm_config_db.is_api,
    }

    # Perform the RAG query
    answer = rag_system.query(
        question=query_input.question,
        document_ids=doc_ids_to_query,
        llm_config=llm_config_for_rag # Pass the correctly structured config
    )

    # Log the query
    db_query_log = QueryLog(
        user_id=current_user.id,
        query_text=query_input.question,
        answer_text=answer,
        queried_documents={"ids": doc_ids_to_query} # Store queried document IDs
    )
    db.add(db_query_log)
    db.commit()
    db.refresh(db_query_log)

    return schemas.QueryOutput(answer=answer, query_id=db_query_log.id)

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
