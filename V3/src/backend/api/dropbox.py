import os
import json
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import dropbox

from src.backend.data.database import get_db
from src.backend.data.models import User, ExternalConnection
from src.backend.api.auth import get_current_active_user, create_access_token
from src.backend.core.security import encrypt_credentials, decrypt_credentials
from src.backend.core.audit import create_audit_log
from src.backend.core.services.dropbox_service import DropboxService

router = APIRouter()

DROPBOX_APP_KEY = os.environ.get("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.environ.get("DROPBOX_APP_SECRET")

def get_dropbox_oauth_flow(request: Request):
    return dropbox.DropboxOAuth2Flow(
        consumer_key=DROPBOX_APP_KEY,
        consumer_secret=DROPBOX_APP_SECRET,
        redirect_uri=str(request.url_for('dropbox_callback')),
        session=request.session,
        csrf_token_session_key="dropbox-auth-csrf-token"
    )

@router.get("/auth/dropbox/login")
def dropbox_login(request: Request, current_user: User = Depends(get_current_active_user)):
    state = create_access_token(data={"user_id": current_user.id})
    authorization_url = get_dropbox_oauth_flow(request).start(state=state)
    return RedirectResponse(authorization_url)

@router.get("/auth/dropbox/callback")
def dropbox_callback(request: Request, db: Session = Depends(get_db)):
    try:
        oauth_result = get_dropbox_oauth_flow(request).finish(request.query_params)
        state_token = request.query_params.get('state')
        payload = jwt.decode(state_token, os.environ.get("SECRET_KEY"), algorithms=[os.environ.get("ALGORITHM", "HS256")])
        user_id = payload.get("user_id")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        credentials_json = json.dumps({
            'access_token': oauth_result.access_token,
            'refresh_token': oauth_result.refresh_token,
            'expires_at': oauth_result.expires_at.isoformat() if oauth_result.expires_at else None,
        })
        encrypted_creds = encrypt_credentials(credentials_json)

        existing_connection = db.query(ExternalConnection).filter_by(user_id=user.id, service_name="dropbox").first()
        if existing_connection:
            existing_connection.encrypted_credentials = encrypted_creds
        else:
            new_connection = ExternalConnection(user_id=user.id, service_name="dropbox", encrypted_credentials=encrypted_creds)
            db.add(new_connection)

        create_audit_log(db, user, "dropbox_connect")
        db.commit()

        return RedirectResponse(url="/pages/11_Connect_Data_Source.py?status=success")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dropbox authentication failed: {e}")

@router.get("/files")
def list_dropbox_files(
    path: str = '',
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    connection = db.query(ExternalConnection).filter_by(user_id=current_user.id, service_name="dropbox").first()
    if not connection:
        raise HTTPException(status_code=400, detail="Dropbox account not connected.")

    try:
        dropbox_service = DropboxService(connection.encrypted_credentials)
        files = dropbox_service.list_files(path=path)
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list Dropbox files: {e}")
