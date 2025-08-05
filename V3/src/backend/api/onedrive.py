import os
import json
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from msal import ConfidentialClientApplication

from src.backend.data.database import get_db
from src.backend.data.models import User, ExternalConnection
from src.backend.api.auth import get_current_active_user, create_access_token
from src.backend.core.security import encrypt_credentials
from src.backend.core.audit import create_audit_log
from src.backend.core.services.onedrive_service import OneDriveService

router = APIRouter()

ONEDRIVE_CLIENT_ID = os.environ.get("ONEDRIVE_CLIENT_ID")
ONEDRIVE_CLIENT_SECRET = os.environ.get("ONEDRIVE_CLIENT_SECRET")
ONEDRIVE_AUTHORITY = "https://login.microsoftonline.com/common"
ONEDRIVE_SCOPES = ["Files.Read.All", "User.Read"]

def get_onedrive_oauth_app():
    # ... (same as before)
    pass

@router.get("/auth/onedrive/login")
def onedrive_login(request: Request, current_user: User = Depends(get_current_active_user)):
    # ... (same as before)
    pass

@router.get("/auth/onedrive/callback")
def onedrive_callback(request: Request, db: Session = Depends(get_db)):
    # ... (same as before)
    pass

@router.get("/files")
def list_onedrive_files(
    item_id: str = 'root',
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    connection = db.query(ExternalConnection).filter_by(user_id=current_user.id, service_name="onedrive").first()
    if not connection:
        raise HTTPException(status_code=400, detail="OneDrive account not connected.")

    try:
        onedrive_service = OneDriveService(connection.encrypted_credentials)
        files = onedrive_service.list_files(item_id=item_id)
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list OneDrive files: {e}")
