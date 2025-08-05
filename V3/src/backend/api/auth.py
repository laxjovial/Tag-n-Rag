import os
import json
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.backend.data import schemas
from src.backend.data.database import get_db
from src.backend.data.models import User, ExternalConnection
from src.backend.core.audit import create_audit_log
from src.backend.core.security import encrypt_credentials

router = APIRouter()

# ... (rest of auth file is the same up to the Google OAuth part)

# --- Google OAuth2 ---
CLIENT_SECRETS_FILE = "client_secrets.json"
SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/userinfo.profile', 'openid']

@router.get("/google/login")
async def google_login(current_user: User = Depends(get_current_active_user)):
    """
    Redirects the user to Google's OAuth 2.0 server.
    We pass the user's ID in the state token to link the account on callback.
    """
    state_token = create_access_token(data={"user_id": current_user.id}, expires_delta=timedelta(minutes=15))

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES,
        redirect_uri="http://localhost:8000/auth/google/callback" # Must match exactly what's in Google Cloud Console
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        state=state_token # Pass our own state token
    )
    return RedirectResponse(authorization_url)

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """
    Handles the callback from Google, exchanges the code for credentials,
    encrypts them, and saves them as a new ExternalConnection.
    """
    state = request.query_params.get('state')
    try:
        payload = jwt.decode(state, os.environ.get("SECRET_KEY"), algorithms=[os.environ.get("ALGORITHM", "HS256")])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=400, detail="Invalid state token")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid state token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES,
        redirect_uri="http://localhost:8000/auth/google/callback"
    )

    flow.fetch_token(authorization_response=str(request.url))

    # Convert credentials to a JSON string, then encrypt
    credentials_json = flow.credentials.to_json()
    encrypted_creds = encrypt_credentials(credentials_json)

    # Check if a connection for this user and service already exists
    existing_connection = db.query(ExternalConnection).filter_by(user_id=user.id, service_name="google_drive").first()
    if existing_connection:
        existing_connection.encrypted_credentials = encrypted_creds
    else:
        new_connection = ExternalConnection(
            user_id=user.id,
            service_name="google_drive",
            encrypted_credentials=encrypted_creds
        )
        db.add(new_connection)

    create_audit_log(db, user, "gdrive_connect")
    db.commit()

    # Redirect user to a success page in the frontend
    return RedirectResponse(url="/pages/11_Connect_Data_Source.py?status=success")
