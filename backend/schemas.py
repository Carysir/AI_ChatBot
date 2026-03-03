"""Pydantic 数据模型"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# ========== 用户相关 ==========
class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[EmailStr] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ========== 对话相关 ==========
class ConversationCreate(BaseModel):
    title: Optional[str] = "新对话"


class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    content: str
    conversation_id: Optional[int] = None
    kb_id: Optional[int] = None  # 指定知识库进行问答


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    intent: Optional[str] = None
    sources: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    message: MessageResponse
    conversation_id: int


# ========== 知识库相关 ==========
class KnowledgeBaseCreate(BaseModel):
    name: str
    description: Optional[str] = None


class KnowledgeBaseResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    doc_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: int
    filename: str
    chunk_count: int
    created_at: datetime

    class Config:
        from_attributes = True
