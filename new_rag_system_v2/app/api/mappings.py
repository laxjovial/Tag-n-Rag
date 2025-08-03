from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import schemas
from ..database import get_db
from ..models import User, Category, GoogleDriveFolderMapping
from .auth import get_current_active_user

router = APIRouter()

class MappingCreate(schemas.BaseModel):
    category_id: int
    folder_id: str
    folder_name: str

class MappingOut(schemas.BaseModel):
    id: int
    category_id: int
    category_name: str
    folder_id: str
    folder_name: str

    class Config:
        orm_mode = True

@router.get("/", response_model=List[MappingOut])
def get_mappings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    mappings = db.query(GoogleDriveFolderMapping).filter(GoogleDriveFolderMapping.user_id == current_user.id).all()
    # We need to get the category name for the output schema
    mappings_out = []
    for mapping in mappings:
        mappings_out.append(MappingOut(
            id=mapping.id,
            category_id=mapping.category_id,
            category_name=mapping.category.name,
            folder_id=mapping.folder_id,
            folder_name=mapping.folder_name
        ))
    return mappings_out

@router.post("/", response_model=schemas.BaseModel) # No specific output model needed
def create_mapping(
    mapping_data: MappingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if the category exists and is owned by the user
    category = db.query(Category).filter(Category.id == mapping_data.category_id, Category.user_id == current_user.id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")

    # Check if the category is already mapped
    if category.gdrive_mapping:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This category is already mapped to a Google Drive folder.")

    new_mapping = GoogleDriveFolderMapping(
        user_id=current_user.id,
        category_id=mapping_data.category_id,
        folder_id=mapping_data.folder_id,
        folder_name=mapping_data.folder_name
    )
    db.add(new_mapping)
    db.commit()
    return {"message": "Mapping created successfully."}

@router.delete("/{mapping_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mapping(
    mapping_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    mapping = db.query(GoogleDriveFolderMapping).filter(GoogleDriveFolderMapping.id == mapping_id, GoogleDriveFolderMapping.user_id == current_user.id).first()
    if not mapping:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mapping not found.")

    db.delete(mapping)
    db.commit()
    return None
