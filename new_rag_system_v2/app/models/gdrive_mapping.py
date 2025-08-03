from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class GoogleDriveFolderMapping(Base):
    __tablename__ = "gdrive_folder_mappings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, unique=True) # A category can only be mapped once
    folder_id = Column(String, nullable=False)
    folder_name = Column(String, nullable=False)

    owner = relationship("User")
    category = relationship("Category", back_populates="gdrive_mapping")
