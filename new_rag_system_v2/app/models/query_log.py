import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from ..database import Base

class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query_text = Column(String, nullable=False)
    answer_text = Column(String, nullable=False)
    queried_documents = Column(JSON, nullable=False) # Store a list of document IDs
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="queries")
