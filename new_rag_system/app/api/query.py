from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import io

from .. import schemas
from ..database import get_db
from ..models import QueryLog, User, Document, Category, LLMConfig
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
    doc_ids_to_query = []
    if query_input.category_id:
        category = db.query(Category).filter(Category.id == query_input.category_id).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        doc_ids_to_query = [doc.id for doc in category.documents]
    elif query_input.document_ids:
        doc_ids_to_query = query_input.document_ids
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Either category_id or document_ids must be provided.")

    if not doc_ids_to_query:
        return schemas.QueryOutput(answer="No documents found to query.", query_id=0)

    llm_config_db = db.query(LLMConfig).filter(LLMConfig.id == query_input.llm_config_id).first() if query_input.llm_config_id else db.query(LLMConfig).filter(LLMConfig.is_default == True).first()
    if not llm_config_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No LLM configuration found. Please select one or set a default.")

    llm_config = {
        "name": llm_config_db.name,
        "model_name": llm_config_db.model_name,
        "api_endpoint": llm_config_db.api_endpoint,
        "api_key_env": llm_config_db.api_key_env,
        "is_api": llm_config_db.is_api,
    }

    answer = rag_system.query(
        question=query_input.question,
        document_ids=doc_ids_to_query,
        llm_config=llm_config
    )

    db_query_log = QueryLog(
        user_id=current_user.id,
        query_text=query_input.question,
        answer_text=answer,
        queried_documents={"ids": doc_ids_to_query}
    )
    db.add(db_query_log)
    db.commit()
    db.refresh(db_query_log)

    return schemas.QueryOutput(answer=answer, query_id=db_query_log.id)

@router.post("/{query_id}/save_as_document", response_model=schemas.DocumentOut)
def save_query_as_document(
    query_id: int,
    new_filename: str,
    category_ids: Optional[List[int]] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query_log = db.query(QueryLog).filter(QueryLog.id == query_id, QueryLog.user_id == current_user.id).first()
    if not query_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Query not found")

    content = f"Question: {query_log.query_text}\n\nAnswer: {query_log.answer_text}"
    file_buffer = export_service.to_txt(content)
    mock_upload_file = io.BytesIO(file_buffer.getvalue()) # Create a BytesIO object for upload

    unique_filename = f"{uuid.uuid4()}_{new_filename}"
    storage_service.upload(file=mock_upload_file, destination_filename=unique_filename)

    categories = []
    if category_ids:
        categories = db.query(Category).filter(Category.id.in_(category_ids)).all()

    db_document = Document(
        filename=unique_filename,
        original_filename=new_filename,
        owner_id=current_user.id,
        categories=categories,
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    rag_system.process_document(document_id=db_document.id, document_text=content)
    return db_document

@router.get("/{query_id}/export")
def export_query_result(
    query_id: int,
    format: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query_log = db.query(QueryLog).filter(QueryLog.id == query_id, QueryLog.user_id == current_user.id).first()
    if not query_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Query not found")

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
        file_buffer,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
