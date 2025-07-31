import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# For simplicity, we'll use a local SQLite database.
# This can be easily swapped out for PostgreSQL in a production environment.
SQLALCHEMY_DATABASE_URL = "sqlite:///./rag_system.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False) # "user" or "admin"

    documents = relationship("Document", back_populates="owner")
    queries = relationship("QueryLog", back_populates="user")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    parent_document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="documents")
    parent_document = relationship("Document", remote_side=[id])

class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query_text = Column(String, nullable=False)
    queried_documents = Column(JSON, nullable=False) # Store a list of document IDs
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="queries")

class LLMConfig(Base):
    __tablename__ = "llm_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    model_name = Column(String, nullable=True) # For LLMs
    api_endpoint = Column(String, nullable=True) # For external APIs
    api_key_env = Column(String, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    is_api = Column(Boolean, default=False, nullable=False)


def create_db_and_tables():
    """
    Creates the database and all tables defined in the models.
    This should be called once on application startup.
    """
    Base.metadata.create_all(bind=engine)

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
