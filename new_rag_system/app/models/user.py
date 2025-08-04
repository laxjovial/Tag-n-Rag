from sqlalchemy import Column, Integer, String, BigInteger
from sqlalchemy.orm import relationship
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False) # "user" or "admin"
    theme = Column(String, default="light", nullable=False) # "light" or "dark"
    storage_used = Column(BigInteger, default=0, nullable=False) # In bytes

    documents = relationship("Document", back_populates="owner")
    queries = relationship("QueryLog", back_populates="user")
    categories = relationship("Category", back_populates="owner", cascade="all, delete-orphan")
