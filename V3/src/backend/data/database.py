import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./rag_system.db")
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def create_db_and_tables():
    from src.backend.data.models import LLMConfig
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(LLMConfig).count() == 0:
            default_configs = [
                LLMConfig(name="OpenAI GPT-3.5", model_name="gpt-3.5-turbo", api_key_env="OPENAI_API_KEY", is_default=True),
                LLMConfig(name="Anthropic Claude 2", model_name="claude-2", api_key_env="ANTHROPIC_API_KEY"),
                LLMConfig(name="Together AI (Mixtral)", model_name="mistralai/Mixtral-8x7B-Instruct-v0.1", api_key_env="TOGETHER_API_KEY"),
            ]
            db.add_all(default_configs)
            db.commit()
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
