from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..models import QueryLog, User, Document, Category
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

    # 2. Log the query to the database
    db_query_log = QueryLog(
        user_id=current_user.id,
        query_text=query_input.question,
        queried_documents={"ids": doc_ids_to_query}
    )
    db.add(db_query_log)
    db.commit()

    return schemas.QueryOutput(answer=answer)
