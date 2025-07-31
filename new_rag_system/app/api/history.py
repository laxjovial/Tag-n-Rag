from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..models import QueryLog, User
from .auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[schemas.QueryLogOut])
def get_user_query_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get the query history for the current user.
    """
    return db.query(QueryLog).filter(QueryLog.user_id == current_user.id).order_by(QueryLog.created_at.desc()).all()
