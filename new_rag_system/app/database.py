import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

import os

# Load the database URL from environment variables, with a fallback for local development
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./rag_system.db")

# The connect_args are specific to SQLite. We shouldn't use them for other databases.
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

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
