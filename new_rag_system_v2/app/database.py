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
    It also seeds the database with initial LLM configurations if none exist.
    """
    # Import models here to prevent circular dependencies, as models import Base from this file.
    from .models.llm_config import LLMConfig

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if there are any LLM configs already
        if db.query(LLMConfig).count() == 0:
            # Seed the database with default configurations
            default_configs = [
                LLMConfig(
                    name="OpenAI GPT-3.5",
                    model_name="gpt-3.5-turbo",
                    api_key_env="OPENAI_API_KEY",
                    is_default=True,
                    is_api=False
                ),
                LLMConfig(
                    name="Anthropic Claude 2",
                    model_name="claude-2",
                    api_key_env="ANTHROPIC_API_KEY",
                    is_api=False
                ),
                LLMConfig(
                    name="Together AI (Mixtral)",
                    model_name="mistralai/Mixtral-8x7B-Instruct-v0.1",
                    api_key_env="TOGETHER_API_KEY",
                    is_api=False
                ),
            ]
            db.add_all(default_configs)
            db.commit()
    finally:
        db.close()

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
