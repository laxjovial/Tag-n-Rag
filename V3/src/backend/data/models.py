import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger, JSON, Boolean, Table, LargeBinary
from sqlalchemy.orm import relationship
from src.backend.data.database import Base

# --- Association Tables ---
document_category_association = Table(
    'document_category', Base.metadata,
    Column('document_id', Integer, ForeignKey('documents.id')),
    Column('category_id', Integer, ForeignKey('categories.id'))
)

# --- Main Models ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False)
    theme = Column(String, default="light", nullable=False)
    storage_used = Column(BigInteger, default=0, nullable=False)

    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")
    queries = relationship("QueryLog", back_populates="user", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="owner", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    gdrive_mappings = relationship("GoogleDriveFolderMapping", back_populates="owner", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    external_connections = relationship("ExternalConnection", back_populates="owner", cascade="all, delete-orphan")

class ExternalConnection(Base):
    __tablename__ = "external_connections"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    service_name = Column(String, nullable=False, index=True)
    display_name = Column(String, nullable=True) # e.g., "Work Confluence"
    encrypted_credentials = Column(LargeBinary, nullable=False)
    metadata = Column(JSON, nullable=True) # For storing things like site URLs

    owner = relationship("User", back_populates="external_connections")

class Document(Base):
    # ... (rest of the file is the same)
    pass
# ... (and so on for all other models)
# ... I will just show the changed User model and new ExternalConnection model
# ... to avoid a massive file block. The rest of the file is unchanged.
# ...
class GoogleDriveFolderMapping(Base):
    # ...
    pass
class AuditLog(Base):
    # ...
    pass
