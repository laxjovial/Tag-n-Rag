import os
import json
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from requests_oauthlib import OAuth2Session
from jose import jwt

from src.backend.data.database import get_db
from src.backend.data.models import User, ExternalConnection
from src.backend.api.auth import get_current_active_user, create_access_token
from src.backend.core.security import encrypt_credentials
from src.backend.core.audit import create_audit_log
from src.backend.core.services.confluence_service import ConfluenceService

router = APIRouter()

CONFLUENCE_CLIENT_ID = os.environ.get("CONFLUENCE_CLIENT_ID")
CONFLUENCE_CLIENT_SECRET = os.environ.get("CONFLUENCE_CLIENT_SECRET")
CONFLUENCE_AUTHORIZATION_URL = "https://auth.atlassian.com/authorize"
CONFLUENCE_TOKEN_URL = "https://auth.atlassian.com/oauth/token"
CONFLUENCE_SCOPES = ["read:confluence-content.all", "read:confluence-space.summary", "offline_access"]

@router.post("/auth/confluence/login")
def confluence_login(
    request: Request,
    site_url: str = Form(...),
    current_user: User = Depends(get_current_active_user)
):
    state_data = {"user_id": current_user.id, "site_url": site_url}
    state = create_access_token(data=state_data)
    confluence = OAuth2Session(CONFLUENCE_CLIENT_ID, redirect_uri=str(request.url_for('confluence_callback')), scope=CONFLUENCE_SCOPES)
    authorization_url, state = confluence.authorization_url(CONFLUENCE_AUTHORIZATION_URL, state=state)
    request.session['oauth_state'] = state
    return {"authorization_url": authorization_url}

@router.get("/auth/confluence/callback")
def confluence_callback(request: Request, db: Session = Depends(get_db)):
    try:
        state_token = request.query_params.get('state')
        payload = jwt.decode(state_token, os.environ.get("SECRET_KEY"), algorithms=[os.environ.get("ALGORITHM", "HS256")])
        user_id = payload.get("user_id")
        site_url = payload.get("site_url")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        confluence = OAuth2Session(CONFLUENCE_CLIENT_ID, state=request.session['oauth_state'], redirect_uri=str(request.url_for('confluence_callback')))
        token = confluence.fetch_token(CONFLUENCE_TOKEN_URL, client_secret=CONFLUENCE_CLIENT_SECRET, authorization_response=str(request.url))

        credentials_json = json.dumps(token)
        encrypted_creds = encrypt_credentials(credentials_json)

        existing_connection = db.query(ExternalConnection).filter_by(user_id=user.id, service_name="confluence").first()
        if existing_connection:
            existing_connection.encrypted_credentials = encrypted_creds
            existing_connection.metadata = {"site_url": site_url}
        else:
            new_connection = ExternalConnection(
                user_id=user.id,
                service_name="confluence",
                encrypted_credentials=encrypted_creds,
                metadata={"site_url": site_url}
            )
            db.add(new_connection)

        create_audit_log(db, user, "confluence_connect")
        db.commit()
        return RedirectResponse(url="/pages/11_Connect_Data_Source.py?status=success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Confluence authentication failed: {e}")

@router.get("/spaces")
def list_confluence_spaces(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    connection = db.query(ExternalConnection).filter_by(user_id=current_user.id, service_name="confluence").first()
    if not connection:
        raise HTTPException(status_code=400, detail="Confluence account not connected.")

    try:
        confluence_service = ConfluenceService(connection.encrypted_credentials, connection.metadata.get("site_url"))
        spaces = confluence_service.get_all_spaces()
        return spaces
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list Confluence spaces: {e}")
