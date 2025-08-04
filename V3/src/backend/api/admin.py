import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.backend.data import schemas
from src.backend.data.database import get_db
import secrets
from src.backend.data.models import User, LLMConfig, QueryLog, AuditLog
from src.backend.api.auth import get_current_active_user, get_current_admin_user, get_password_hash
from src.backend.core.audit import create_audit_log

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

@router.get("/audit-log/", response_model=List[schemas.AuditLogOut], dependencies=[Depends(get_current_admin_user)])
def get_audit_log(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieves entries from the audit log with pagination.
    """
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()

    # Manually construct the response to include the username
    logs_out = []
    for log in logs:
        log_data = schemas.AuditLogOut.from_orm(log)
        log_data.username = log.user.username if log.user else "System"
        logs_out.append(log_data)

    return logs_out

@router.post("/users/invite", response_model=schemas.UserOut, dependencies=[Depends(get_current_admin_user)])
def invite_user(
    user_invite: schemas.UserInvite,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Creates a new user with a temporary password.
    In a real app, this would also trigger an invitation email.
    """
    if db.query(User).filter(User.username == user_invite.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    temp_password = secrets.token_urlsafe(16)
    hashed_password = get_password_hash(temp_password)

    new_user = User(
        username=user_invite.username,
        hashed_password=hashed_password,
        role="user" # Invited users default to 'user' role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    create_audit_log(db, current_admin, "user_invite", {"invited_user_id": new_user.id, "invited_username": new_user.username})

    # In a real app, you would return the temp password or email it.
    # For now, we return the user object.
    return new_user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_admin_user)])
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user_to_delete.id == current_admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admins cannot delete themselves.")

    create_audit_log(db, current_admin, "user_delete", {"deleted_user_id": user_to_delete.id, "deleted_username": user_to_delete.username})

    db.delete(user_to_delete)
    db.commit()
    return None

@router.put("/users/{user_id}/role", response_model=schemas.UserOut, dependencies=[Depends(get_current_admin_user)])
def update_user_role(
    user_id: int,
    role_update: schemas.UserRoleUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    if role_update.role not in ["user", "admin"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role specified.")

    user_to_update = db.query(User).filter(User.id == user_id).first()
    if not user_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user_to_update.id == current_admin.id and role_update.role == "user":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admins cannot demote themselves.")

    original_role = user_to_update.role
    user_to_update.role = role_update.role

    create_audit_log(db, current_admin, "user_role_update", {
        "target_user_id": user_to_update.id,
        "target_username": user_to_update.username,
        "old_role": original_role,
        "new_role": role_update.role
    })

    db.commit()
    db.refresh(user_to_update)
    return user_to_update
