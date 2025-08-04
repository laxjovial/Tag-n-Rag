import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.backend.data import schemas
from src.backend.data.database import get_db
from src.backend.data.models import User, LLMConfig, QueryLog
from src.backend.api.auth import get_current_active_user, get_current_admin_user

router = APIRouter()

@router.get("/llm_configs/", response_model=List[schemas.LLMConfig], dependencies=[Depends(get_current_admin_user)])
def get_all_llm_configs(db: Session = Depends(get_db)):
    return db.query(LLMConfig).all()

@router.get("/users/", response_model=List[schemas.UserOut], dependencies=[Depends(get_current_admin_user)])
def list_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    limit_mb = int(os.environ.get("USER_STORAGE_LIMIT_MB", 1024))
    storage_limit_bytes = limit_mb * 1024 * 1024
    users_out = []
    for user in users:
        user_data = schemas.UserOut.from_orm(user)
        user_data.storage_limit = storage_limit_bytes
        users_out.append(user_data)
    return users_out

@router.get("/history/", dependencies=[Depends(get_current_admin_user)])
def get_all_query_history(db: Session = Depends(get_db)):
    return db.query(QueryLog).order_by(QueryLog.created_at.desc()).all()

@router.post("/configs/", response_model=schemas.LLMConfig, dependencies=[Depends(get_current_admin_user)])
def create_llm_config(config: schemas.LLMConfigCreate, db: Session = Depends(get_db)):
    if config.is_default:
        existing_default = db.query(LLMConfig).filter(LLMConfig.is_default == True).first()
        if existing_default:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A default LLM config already exists.")
    db_config = LLMConfig(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

@router.get("/analytics/queries_per_day/", dependencies=[Depends(get_current_admin_user)])
def get_queries_per_day(db: Session = Depends(get_db)):
    result = db.query(
        func.date(QueryLog.created_at).label("date"),
        func.count(QueryLog.id).label("query_count")
    ).group_by(func.date(QueryLog.created_at)).order_by(func.date(QueryLog.created_at)).all()
    return [{"date": row.date, "queries": row.query_count} for row in result]

@router.put("/configs/{config_id}", response_model=schemas.LLMConfig, dependencies=[Depends(get_current_admin_user)])
def update_llm_config(config_id: int, config: schemas.LLMConfigCreate, db: Session = Depends(get_db)):
    db_config = db.query(LLMConfig).filter(LLMConfig.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")
    if config.is_default and not db_config.is_default:
        existing_default = db.query(LLMConfig).filter(LLMConfig.is_default == True).first()
        if existing_default and existing_default.id != config_id:
            existing_default.is_default = False
            db.add(existing_default)
    for key, value in config.dict(exclude_unset=True).items():
        setattr(db_config, key, value)
    db.commit()
    db.refresh(db_config)
    return db_config

@router.delete("/configs/{config_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_admin_user)])
def delete_llm_config(config_id: int, db: Session = Depends(get_db)):
    db_config = db.query(LLMConfig).filter(LLMConfig.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")
    db.delete(db_config)
    db.commit()
    return None
