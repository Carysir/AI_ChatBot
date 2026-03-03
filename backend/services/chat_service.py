"""对话管理服务"""
import json
from typing import Optional

from sqlalchemy.orm import Session

from backend.models import Conversation, Message
from backend.services.llm_service import llm_service
from backend.services.rag_service import rag_service


class ChatService:
    """对话管理服务"""

    def process_message(
        self,
        db: Session,
        user_id: int,
        content: str,
        conversation_id: Optional[int] = None,
        kb_id: Optional[int] = None,
    ) -> dict:
        """处理用户消息并生成回复"""
        # 1. 获取或创建会话
        if conversation_id:
            conversation = (
                db.query(Conversation)
                .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)
                .first()
            )
            if not conversation:
                raise ValueError("会话不存在")
        else:
            conversation = Conversation(user_id=user_id, title=content[:50])
            db.add(conversation)
            db.flush()

        # 2. 保存用户消息
        user_msg = Message(
            conversation_id=conversation.id,
            role="user",
            content=content,
        )
        db.add(user_msg)
        db.flush()

        # 3. 意图识别
        intent = llm_service.classify_intent(content)
        user_msg.intent = intent

        # 4. 获取历史对话
        history = self._get_history(db, conversation.id)

        # 5. 根据意图路由处理
        sources = None
        if kb_id and intent in ("qa", "task"):
            # 知识库问答
            reply, sources = self._handle_kb_qa(content, kb_id, history)
        elif intent == "chat":
            reply = self._handle_chat(content, history)
        elif intent == "task":
            reply = self._handle_task(content, history)
        else:
            reply = self._handle_chat(content, history)

        # 6. 保存助手回复
        assistant_msg = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=reply,
            intent=intent,
            sources=json.dumps(sources, ensure_ascii=False) if sources else None,
        )
        db.add(assistant_msg)
        db.commit()
        db.refresh(assistant_msg)

        return {
            "message": assistant_msg,
            "conversation_id": conversation.id,
        }

    def _get_history(self, db: Session, conversation_id: int, limit: int = 10) -> list[dict]:
        """获取对话历史"""
        messages = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .all()
        )
        messages.reverse()
        return [{"role": msg.role, "content": msg.content} for msg in messages if msg.role != "system"]

    def _handle_kb_qa(self, query: str, kb_id: int, history: list[dict]) -> tuple[str, list]:
        """知识库问答"""
        # RAG 检索
        docs = rag_service.search(kb_id, query)
        if not docs:
            reply = llm_service.chat(
                [{"role": "system", "content": "你是一个友好的助手。知识库中没有找到相关内容，请根据你的知识尝试回答。"}]
                + history[-6:]
                + [{"role": "user", "content": query}]
            )
            return reply, []

        # 带上下文的 LLM 回答
        reply = llm_service.chat_with_context(query, docs, history)
        sources = [{"content": d["content"][:100], "score": d["score"]} for d in docs]
        return reply, sources

    def _handle_chat(self, query: str, history: list[dict]) -> str:
        """闲聊处理"""
        messages = [
            {"role": "system", "content": "你是一个友好、幽默的聊天助手。请用自然的方式回复用户。"}
        ] + history[-6:] + [{"role": "user", "content": query}]
        return llm_service.chat(messages)

    def _handle_task(self, query: str, history: list[dict]) -> str:
        """任务型处理"""
        messages = [
            {"role": "system", "content": "你是一个高效的任务助手，擅长翻译、总结、写作、代码等任务。请认真完成用户的要求。"}
        ] + history[-6:] + [{"role": "user", "content": query}]
        return llm_service.chat(messages)


# 全局实例
chat_service = ChatService()
