"""对话相关路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models import Conversation, Message, User
from backend.schemas import (
    ChatResponse,
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
)
from backend.services.chat_service import chat_service

router = APIRouter(prefix="/api/chat", tags=["对话管理"])


@router.post("/send", response_model=ChatResponse)
def send_message(
    data: MessageCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """发送消息并获取回复"""
    try:
        result = chat_service.process_message(
            db=db,
            user_id=user.id,
            content=data.content,
            conversation_id=data.conversation_id,
            kb_id=data.kb_id,
        )
        return ChatResponse(
            message=result["message"],
            conversation_id=result["conversation_id"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/conversations", response_model=list[ConversationResponse])
def list_conversations(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户的所有会话"""
    conversations = (
        db.query(Conversation)
        .filter(Conversation.user_id == user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )
    return conversations


@router.post("/conversations", response_model=ConversationResponse)
def create_conversation(
    data: ConversationCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建新会话"""
    conv = Conversation(user_id=user.id, title=data.title)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


@router.get("/conversations/{conv_id}/messages", response_model=list[MessageResponse])
def get_messages(
    conv_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取会话的所有消息"""
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conv_id, Conversation.user_id == user.id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="会话不存在")

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conv_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    return messages


@router.delete("/conversations/{conv_id}")
def delete_conversation(
    conv_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除会话"""
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conv_id, Conversation.user_id == user.id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="会话不存在")

    db.delete(conv)
    db.commit()
    return {"message": "删除成功"}
