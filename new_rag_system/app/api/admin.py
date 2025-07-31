from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db, User, LLMConfig, QueryLog
from .auth import get_current_active_user

router = APIRouter()

# --- Dependency for Admin Users ---
def get_current_admin_user(current_user: User = Depends(get_current_active_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges",
        )
    return current_user

# --- Admin Endpoints ---
@router.get("/users", response_model=List[schemas.UserOut], dependencies=[Depends(get_current_admin_user)])
def list_all_users(db: Session = Depends(get_db)):
    """
    Get a list of all users in the system. (Admin only)
    """
    return db.query(User).all()

@router.get("/history", dependencies=[Depends(get_current_admin_user)])
def get_all_query_history(db: Session = Depends(get_db)):
    """
    Get the query history for all users. (Admin only)
    """
    return db.query(QueryLog).order_by(QueryLog.created_at.desc()).all()

@router.post("/configs", response_model=schemas.LLMConfig, dependencies=[Depends(get_current_admin_user)])
def create_llm_config(config: schemas.LLMConfig, db: Session = Depends(get_db)):
    """
    Create a new LLM or API configuration. (Admin only)
    """
    db_config = LLMConfig(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

@router.get("/configs", response_model=List[schemas.LLMConfig], dependencies=[Depends(get_current_admin_user)])
def get_all_llm_configs(db: Session = Depends(get_db)):
    """
    Get all LLM and API configurations. (Admin only)
    """
    return db.query(LLMConfig).all()

@router.put("/configs/{config_id}", response_model=schemas.LLMConfig, dependencies=[Depends(get_current_admin_user)])
def update_llm_config(config_id: int, config: schemas.LLMConfig, db: Session = Depends(get_db)):
    """
    Update an LLM or API configuration. (Admin only)
    """
    db_config = db.query(LLMConfig).filter(LLMConfig.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")

    for key, value in config.dict().items():
        setattr(db_config, key, value)

    db.commit()
    db.refresh(db_config)
    return db_config
