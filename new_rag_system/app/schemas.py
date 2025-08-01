from pydantic import BaseModel, ConfigDict # Added ConfigDict
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

    model_config = ConfigDict(from_attributes=True) # Updated

# --- Category Schemas ---
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True) # Updated

# --- Notification Schemas ---
class NotificationOut(BaseModel):
    id: int
    message: str
    is_read: bool
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True) # Updated

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
    original_filename: str
    version: int
    owner_id: int
    created_at: datetime.datetime
    expires_at: Optional[datetime.datetime] = None

    model_config = ConfigDict(from_attributes=True) # Updated

class DocumentUpdate(BaseModel):
    content: str

class DocumentCreateFromText(BaseModel):
    filename: str
    content: str
    category_ids: Optional[list[int]] = None

# --- Query Schemas ---
class QueryInput(BaseModel):
    question: str
    document_ids: Optional[list[int]] = None
    category_id: Optional[int] = None
    llm_config_id: Optional[int] = None

class QueryOutput(BaseModel):
    answer: str
    query_id: int

class QueryLogOut(BaseModel):
    id: int
    query_text: str
    answer_text: str
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True) # Updated

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

class LLMConfig(LLMConfigBase):
    id: int

    model_config = ConfigDict(from_attributes=True) # Updated

# --- Setting Schemas ---
class SettingBase(BaseModel):
    key: str
    value: str

class SettingCreate(SettingBase):
    pass

class SettingOut(SettingBase):
    id: int

    model_config = ConfigDict(from_attributes=True) # Updated
