from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..models import QueryLog, User
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
    Performs a RAG query on a set of documents.
    """
    # 1. Perform the query using the RAG system
    answer = rag_system.query(
        question=query_input.question,
        document_ids=query_input.document_ids
    )

    # 2. Log the query to the database
    db_query_log = QueryLog(
        user_id=current_user.id,
        query_text=query_input.question,
        queried_documents={"ids": query_input.document_ids}
    )
    db.add(db_query_log)
    db.commit()

    return schemas.QueryOutput(answer=answer)
