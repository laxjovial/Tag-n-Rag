from pydantic import BaseModel
from typing import Optional
import datetime

# --- User Schemas ---
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    role: str

    class Config:
        orm_mode = True

# --- Category Schemas ---
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: int

    class Config:
        orm_mode = True

# --- Notification Schemas ---
class NotificationOut(BaseModel):
    id: int
    message: str
    is_read: bool
    created_at: datetime.datetime

    class Config:
        orm_mode = True

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- Document Schemas ---
class DocumentOut(BaseModel):
    id: int
    filename: str
    version: int
    owner_id: int
    created_at: datetime.datetime
    expires_at: Optional[datetime.datetime] = None

    class Config:
        orm_mode = True

# --- Query Schemas ---
class QueryInput(BaseModel):
    question: str
    document_ids: Optional[list[int]] = None
    category_id: Optional[int] = None

class QueryOutput(BaseModel):
    answer: str

# --- LLM/API Config Schemas ---
class LLMConfigBase(BaseModel):
    name: str
    model_name: Optional[str] = None
    api_endpoint: Optional[str] = None
    api_key_env: str
    is_default: bool = False
    is_api: bool = False

class LLMConfigCreate(LLMConfigBase):
    pass

class LLMConfigOut(LLMConfigBase):
    id: int

    class Config:
        orm_mode = True
