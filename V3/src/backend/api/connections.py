from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.backend.data import schemas
from src.backend.data.database import get_db
from src.backend.data.models import User, ExternalConnection
from src.backend.api.auth import get_current_active_user
from src.backend.core.audit import create_audit_log

router = APIRouter()

class ConnectionOut(schemas.BaseModel):
    id: int
    service_name: str

@router.get("/", response_model=List[ConnectionOut])
def get_user_connections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Lists all of the user's external service connections."""
    connections = db.query(ExternalConnection).filter(ExternalConnection.user_id == current_user.id).all()
    return connections

@router.delete("/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_connection(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Deletes a user's external service connection."""
    connection = db.query(ExternalConnection).filter(
        ExternalConnection.id == connection_id,
        ExternalConnection.user_id == current_user.id
    ).first()

    if not connection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found.")

    create_audit_log(db, current_user, "connection_delete", {"service_name": connection.service_name})

    db.delete(connection)
    db.commit()
    return None
