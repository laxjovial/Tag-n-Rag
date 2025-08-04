from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.backend.data import schemas
from src.backend.data.database import get_db
from src.backend.data.models import QueryLog, User
from src.backend.api.auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[schemas.QueryLogOut])
def get_user_query_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = 100,
):
    """
    Get the query history for the current user.
    """
    return db.query(QueryLog).filter(QueryLog.user_id == current_user.id).order_by(QueryLog.created_at.desc()).limit(limit).all()

@router.get("/analytics", response_model=schemas.UserAnalytics)
def get_user_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get personal analytics for the current user.
    """
    total_queries = db.query(QueryLog).filter(QueryLog.user_id == current_user.id).count()

    queries_per_day = db.query(
        func.date(QueryLog.created_at).label("date"),
        func.count(QueryLog.id).label("query_count")
    ).filter(QueryLog.user_id == current_user.id).group_by(func.date(QueryLog.created_at)).order_by(func.date(QueryLog.created_at)).all()

    top_documents_query = db.query(
        QueryLog.document_id,
        func.count(QueryLog.document_id).label('count')
    ).filter(QueryLog.user_id == current_user.id).group_by(QueryLog.document_id).order_by(func.count(QueryLog.document_id).desc()).limit(5).all()

    return {
        "total_queries": total_queries,
        "queries_per_day": [{"date": str(row.date), "queries": row.query_count} for row in queries_per_day],
        "top_documents": [{"document_id": row.document_id, "count": row.count} for row in top_documents_query]
    }
