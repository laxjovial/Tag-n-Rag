import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from ..database import Base
from .category import document_category_association

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True, nullable=False) # This will be the unique name in storage
    original_filename = Column(String, index=True, nullable=False) # The original name for display
    version = Column(Integer, default=1, nullable=False)
    parent_document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    size = Column(BigInteger, nullable=False) # Size in bytes

    owner = relationship("User", back_populates="documents")
    parent_document = relationship("Document", remote_side=[id])

    categories = relationship(
        "Category",
        secondary=document_category_association,
        back_populates="documents"
    )
