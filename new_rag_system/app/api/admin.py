from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func # For analytics functions

from .. import schemas
from ..database import get_db
from ..models import User, LLMConfig, QueryLog
from .auth import get_current_active_user, get_current_admin_user

router = APIRouter()

# --- Publicly Accessible (Authenticated) LLM Config Endpoint ---
@router.get("/llm_configs/", response_model=List[schemas.LLMConfig], dependencies=[Depends(get_current_admin_user)])
def get_all_llm_configs(db: Session = Depends(get_db)):
    """
    Get all LLM and API configurations. (Admin only)
    """
    return db.query(LLMConfig).all()

# --- Admin-Only Endpoints ---
@router.get("/users/", response_model=List[schemas.UserOut], dependencies=[Depends(get_current_admin_user)])
def list_all_users(db: Session = Depends(get_db)):
    """
    Get a list of all users in the system. (Admin only)
    """
    return db.query(User).all()

@router.get("/history/", dependencies=[Depends(get_current_admin_user)])
def get_all_query_history(db: Session = Depends(get_db)):
    """
    Get the query history for all users. (Admin only)
    """
    return db.query(QueryLog).order_by(QueryLog.created_at.desc()).all()

@router.post("/configs/", response_model=schemas.LLMConfig, dependencies=[Depends(get_current_admin_user)])
def create_llm_config(config: schemas.LLMConfigCreate, db: Session = Depends(get_db)): # Use LLMConfigCreate
    """
    Create a new LLM or API configuration. (Admin only)
    """
    # Check if a default config already exists if this one is set as default
    if config.is_default:
        existing_default = db.query(LLMConfig).filter(LLMConfig.is_default == True).first()
        if existing_default:
            # Optionally, you could set the old default to False here
            # existing_default.is_default = False
            # db.add(existing_default)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A default LLM config already exists. Please unset it first or update it.")

    db_config = LLMConfig(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

@router.get("/analytics/queries_per_day/", dependencies=[Depends(get_current_admin_user)])
def get_queries_per_day(db: Session = Depends(get_db)):
    """
    Get the number of queries per day. (Admin only)
    """
    result = db.query(
        func.date(QueryLog.created_at).label("date"),
        func.count(QueryLog.id).label("query_count")
    ).group_by(func.date(QueryLog.created_at)).order_by(func.date(QueryLog.created_at)).all()

    return [{"date": row.date, "queries": row.query_count} for row in result]

@router.put("/configs/{config_id}", response_model=schemas.LLMConfig, dependencies=[Depends(get_current_admin_user)])
def update_llm_config(config_id: int, config: schemas.LLMConfigCreate, db: Session = Depends(get_db)): # Use LLMConfigCreate
    """
    Update an LLM or API configuration. (Admin only)
    """
    db_config = db.query(LLMConfig).filter(LLMConfig.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")

    # Handle setting a new default
    if config.is_default and not db_config.is_default:
        existing_default = db.query(LLMConfig).filter(LLMConfig.is_default == True).first()
        if existing_default and existing_default.id != config_id:
            existing_default.is_default = False # Unset old default
            db.add(existing_default)

    for key, value in config.dict(exclude_unset=True).items(): # Use exclude_unset to only update provided fields
        setattr(db_config, key, value)

    db.commit()
    db.refresh(db_config)
    return db_config

@router.delete("/configs/{config_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_admin_user)])
def delete_llm_config(config_id: int, db: Session = Depends(get_db)):
    """
    Delete an LLM or API configuration. (Admin only)
    """
    db_config = db.query(LLMConfig).filter(LLMConfig.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")

    db.delete(db_config)
    db.commit()
    return None
