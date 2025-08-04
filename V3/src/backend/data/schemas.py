from pydantic import BaseModel, ConfigDict # Added ConfigDict
from typing import Optional
import datetime

# --- User Schemas ---
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserInvite(BaseModel):
    email: str # In a real app, this would be used to send an invite. For now, it's a placeholder.
    username: str

class UserRoleUpdate(BaseModel):
    role: str

class UserOut(UserBase):
    id: int
    role: str
    has_google_credentials: bool = False
    storage_used: int # In bytes
    storage_limit: int # In bytes

    model_config = ConfigDict(from_attributes=True)

# --- Category Schemas ---
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True) # Updated

# --- Analytics Schemas ---
from typing import List

class QueriesPerDay(BaseModel):
    date: str
    queries: int

class TopDocument(BaseModel):
    document_id: int
    count: int

class UserAnalytics(BaseModel):
    total_queries: int
    queries_per_day: List[QueriesPerDay]
    top_documents: List[TopDocument]

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

class DocumentAppend(BaseModel):
    query_id: int
    formatting_method: str # e.g., 'simple', 'informative', 'structured'

class GoogleDriveIngestRequest(BaseModel):
    file_ids: List[str]

# --- Audit Log Schemas ---
class AuditLogOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None # For easy display
    action: str
    details: Optional[dict] = None
    timestamp: datetime.datetime

    class Config:
        orm_mode = True

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
    conversation_id: Optional[str] = None

class QueryOutput(BaseModel):
    answer: str
    query_id: int
    conversation_id: str

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
