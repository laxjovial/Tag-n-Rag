from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..models import QueryLog, User, Document, Category
from ..services.export import ExportService
from .auth import get_current_active_user
from .documents import rag_system # Import the shared RAG system instance

router = APIRouter()

@router.post("/", response_model=schemas.QueryOutput)
def query_documents(
    query_input: schemas.QueryInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Performs a RAG query on a set of documents or a category.
    """
    doc_ids_to_query = []

    if query_input.category_id:
        # If a category is specified, get all document IDs in that category
        category = db.query(Category).filter(Category.id == query_input.category_id).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        doc_ids_to_query = [doc.id for doc in category.documents]
    elif query_input.document_ids:
        # Otherwise, use the provided list of document IDs
        doc_ids_to_query = query_input.document_ids
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either category_id or document_ids must be provided."
        )

    if not doc_ids_to_query:
        return schemas.QueryOutput(answer="No documents found in the specified category to query.")

    # 1. Perform the query using the RAG system
    answer = rag_system.query(
        question=query_input.question,
        document_ids=doc_ids_to_query
    )

    # 2. Log the query and its answer to the database
    db_query_log = QueryLog(
        user_id=current_user.id,
        query_text=query_input.question,
        answer_text=answer,
        queried_documents={"ids": doc_ids_to_query}
    )
    db.add(db_query_log)
    db.commit()

    return schemas.QueryOutput(answer=answer)

@router.post("/{query_id}/save_as_document", response_model=schemas.DocumentOut)
def save_query_as_document(
    query_id: int,
    new_filename: str,
    category_ids: Optional[List[int]] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query_log = db.query(QueryLog).filter(
        QueryLog.id == query_id, QueryLog.user_id == current_user.id
    ).first()

    if not query_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Query not found")

    content = f"Question: {query_log.query_text}\n\nAnswer: {query_log.answer_text}"

    # Use the export service to create a file-like object in memory
    file_buffer = export_service.to_txt(content)

    # Create a mock UploadFile to pass to the storage service
    mock_upload_file = UploadFile(filename=new_filename, file=file_buffer)

    # This is a simplified call to the upload logic. In a real app, this might be
    # refactored into a shared service function to avoid code duplication.
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

export_service = ExportService()

@router.get("/{query_id}/export")
def export_query_result(
    query_id: int,
    format: str, # 'pdf', 'docx', or 'txt'
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query_log = db.query(QueryLog).filter(
        QueryLog.id == query_id, QueryLog.user_id == current_user.id
    ).first()

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
    else: # Default to txt
        file_buffer = export_service.to_txt(content)
        media_type = "text/plain"
        filename = f"query_{query_id}.txt"

    return StreamingResponse(
        file_buffer,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
