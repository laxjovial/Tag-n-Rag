import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..models import User # Ensure User model is imported

router = APIRouter()

# --- Configuration ---
# IMPORTANT: Load SECRET_KEY from environment variables in production.
# The default value here is for development only.
SECRET_KEY = os.environ.get("SECRET_KEY", "0f338d2fa3935e2cd63dc8cd1c0bed86f1fe460f09324211b136a38ee708151f")
ALGORITHM = "HS256" # Algorithm used for JWT signing
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # How long the access token is valid (in minutes)

# --- Security Setup ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# OAuth2PasswordBearer points to the login endpoint where the token can be obtained
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# --- Utility Functions ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes a plain-text password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token.
    'data' should contain claims like 'sub' (subject, e.g., username), 'user_id', 'role'.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Default expiration if not provided (e.g., for testing purposes)
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire}) # Add expiration timestamp to the payload
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Dependency to get current user ---
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Dependency that decodes the JWT token from the Authorization header,
    validates it, and fetches the corresponding user from the database.
    Raises HTTPException 401 if credentials are invalid or token is expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the token using the secret key and algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub") # Get the subject (username) from the payload
        user_id: Optional[int] = payload.get("user_id") # Get user_id if present
        user_role: Optional[str] = payload.get("role") # Get role if present

        if username is None:
            raise credentials_exception

        # You can use token_data for additional checks if needed
        token_data = schemas.TokenData(username=username)

    except JWTError:
        # This catches invalid tokens, expired tokens, etc.
        raise credentials_exception

    # Fetch the user from the database using the username from the token
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception # User not found in DB, token is valid but user doesn't exist

    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency that ensures the current user is active.
    Assumes your User model has a 'disabled' attribute (Boolean).
    """
    # If you have a 'disabled' field in your User model, uncomment and use this:
    # if current_user.disabled:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency that ensures the current user has an 'admin' role.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not an admin user")
    return current_user

# --- API Endpoints ---
@router.post("/register", response_model=schemas.UserOut)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Registers a new user in the system."""
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    hashed_password = get_password_hash(user.password)
    # Assign a default role (e.g., "user") to new registrations
    new_user = User(username=user.username, hashed_password=hashed_password, role="user")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticates a user with username and password, then returns an access token.
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Include user_id and role in the token payload for more detailed authorization checks
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Google OAuth2 ---
# Note: In a real app, 'client_secrets.json' should be handled securely and not be in the repo.
# It should contain the client_id, client_secret, redirect_uris, etc. from your Google Cloud project.
# The user needs to enable the Google Drive API in their Google Cloud project.
CLIENT_SECRETS_FILE = "client_secrets.json"
SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/userinfo.profile']

@router.get("/google/login")
async def google_login(request: Request):
    """
    Redirects the user to Google's OAuth 2.0 server to initiate authentication.
    """
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES,
        redirect_uri=str(request.url_for('google_callback'))
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    # Store the state in the session to prevent CSRF attacks
    request.session['state'] = state
    return RedirectResponse(authorization_url)

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """
    Handles the callback from Google's OAuth 2.0 server.
    """
    state = request.session['state']
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state,
        redirect_uri=str(request.url_for('google_callback'))
    )

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    flow.fetch_token(authorization_response=str(request.url))

    credentials = flow.credentials

    # Get user info from Google
    userinfo_request = google.auth.transport.requests.Request()
    user_info = credentials.to_json() # Contains tokens and other info

    # Here you would typically get the user's Google profile ID and find the
    # corresponding user in your database. For this example, we assume the user
    # is already logged into our app and we are just linking their Google account.
    # We'll use the currently logged-in user for this.
    # Note: A real implementation would need a more robust way to link accounts.
    # This requires the user to be logged into our app first before hitting /google/login.

    # To get the current user, we'd need the JWT. This callback doesn't have it.
    # This flow needs to be adjusted. A common pattern is to pass the user's JWT
    # in the 'state' parameter or have a separate step after login.

    # For now, let's assume we can get the user. This is a placeholder for a real implementation.
    # In a real app, you would decode a JWT from the state or have the user login first.
    # This part of the code will not work without a logged-in user context.

    # Let's stub this out for now. We will need to revisit this logic.
    # The user would need to be logged in first.

    # For now, we will just return a success message.
    # The credentials would be saved to the user model:
    # current_user.google_credentials = json.loads(credentials.to_json())
    # db.commit()

    return {"message": "Google account linked successfully. Credentials would be stored here."}
