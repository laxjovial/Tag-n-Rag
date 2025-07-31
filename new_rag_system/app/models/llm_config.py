from sqlalchemy import Column, Integer, String, Boolean
from ..database import Base

class LLMConfig(Base):
    __tablename__ = "llm_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    model_name = Column(String, nullable=True) # For LLMs
    api_endpoint = Column(String, nullable=True) # For external APIs
    api_key_env = Column(String, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    is_api = Column(Boolean, default=False, nullable=False)
