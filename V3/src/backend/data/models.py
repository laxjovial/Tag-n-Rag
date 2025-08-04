import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger, JSON, Boolean, Table
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
    google_credentials = Column(JSON, nullable=True)
    storage_used = Column(BigInteger, default=0, nullable=False)

    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")
    queries = relationship("QueryLog", back_populates="user", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="owner", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    gdrive_mappings = relationship("GoogleDriveFolderMapping", back_populates="owner", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True, nullable=False)
    original_filename = Column(String, index=True, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    size = Column(BigInteger, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="documents")
    categories = relationship("Category", secondary=document_category_association, back_populates="documents")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="categories")
    documents = relationship("Document", secondary=document_category_association, back_populates="documents")
    gdrive_mapping = relationship("GoogleDriveFolderMapping", back_populates="category", uselist=False, cascade="all, delete-orphan")

class QueryLog(Base):
    __tablename__ = "query_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query_text = Column(String, nullable=False)
    answer_text = Column(String, nullable=False)
    queried_documents = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="queries")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="notifications")

class LLMConfig(Base):
    __tablename__ = "llm_configs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    model_name = Column(String, nullable=True)
    api_endpoint = Column(String, nullable=True)
    api_key_env = Column(String, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    is_api = Column(Boolean, default=False, nullable=False)

class Setting(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(String, nullable=False)

class GoogleDriveFolderMapping(Base):
    __tablename__ = "gdrive_folder_mappings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, unique=True)
    folder_id = Column(String, nullable=False)
    folder_name = Column(String, nullable=False)

    owner = relationship("User", back_populates="gdrive_mappings")
    category = relationship("Category", back_populates="gdrive_mapping")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True) # Nullable for system actions
    action = Column(String, nullable=False, index=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    user = relationship("User", back_populates="audit_logs")
