import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..models import User
from .auth import get_current_active_user

router = APIRouter()

@router.get("/me", response_model=schemas.UserOut)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    user_data = schemas.UserOut.from_orm(current_user)
    user_data.has_google_credentials = current_user.google_credentials is not None

    # Get storage limit from environment variable
    limit_mb = int(os.environ.get("USER_STORAGE_LIMIT_MB", 1024))
    user_data.storage_limit = limit_mb * 1024 * 1024

    return user_data

class UserThemeUpdate(schemas.BaseModel):
    theme: str

@router.put("/profile/theme", response_model=schemas.UserOut)
def update_user_theme(
    theme_data: UserThemeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update the theme preference for the current user.
    """
    if theme_data.theme not in ["light", "dark"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid theme")

    current_user.theme = theme_data.theme
    db.commit()
    db.refresh(current_user)
    return current_user
