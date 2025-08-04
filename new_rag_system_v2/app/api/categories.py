from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..models import Category, User
from .auth import get_current_active_user

router = APIRouter()

@router.post("/", response_model=schemas.CategoryOut)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new category for the current user.
    """
    # Check if category with the same name already exists for this user
    existing_category = db.query(Category).filter(
        Category.name == category.name,
        Category.user_id == current_user.id
    ).first()
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists."
        )

    db_category = Category(**category.dict(), user_id=current_user.id)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/", response_model=List[schemas.CategoryOut])
def get_user_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get all categories for the current user.
    """
    return db.query(Category).filter(Category.user_id == current_user.id).all()

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a category owned by the current user.
    """
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found or you do not have permission to delete it."
        )

    db.delete(category)
    db.commit()
    return None
