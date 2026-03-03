"""知识库相关路由"""
import os

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.config import settings
from backend.database import get_db
from backend.models import Document, KnowledgeBase, User
from backend.schemas import DocumentResponse, KnowledgeBaseCreate, KnowledgeBaseResponse
from backend.services.rag_service import rag_service

router = APIRouter(prefix="/api/kb", tags=["知识库管理"])


@router.post("", response_model=KnowledgeBaseResponse)
def create_kb(
    data: KnowledgeBaseCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建知识库"""
    kb = KnowledgeBase(name=data.name, description=data.description, user_id=user.id)
    db.add(kb)
    db.commit()
    db.refresh(kb)
    return KnowledgeBaseResponse(
        id=kb.id,
        name=kb.name,
        description=kb.description,
        doc_count=0,
        created_at=kb.created_at,
    )


@router.get("", response_model=list[KnowledgeBaseResponse])
def list_kbs(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户的所有知识库"""
    kbs = db.query(KnowledgeBase).filter(KnowledgeBase.user_id == user.id).all()
    result = []
    for kb in kbs:
        doc_count = db.query(Document).filter(Document.kb_id == kb.id).count()
        result.append(
            KnowledgeBaseResponse(
                id=kb.id,
                name=kb.name,
                description=kb.description,
                doc_count=doc_count,
                created_at=kb.created_at,
            )
        )
    return result


@router.delete("/{kb_id}")
def delete_kb(
    kb_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除知识库"""
    kb = (
        db.query(KnowledgeBase)
        .filter(KnowledgeBase.id == kb_id, KnowledgeBase.user_id == user.id)
        .first()
    )
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")

    rag_service.delete_kb(kb_id)
    db.delete(kb)
    db.commit()
    return {"message": "删除成功"}


@router.post("/{kb_id}/upload", response_model=DocumentResponse)
async def upload_document(
    kb_id: int,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """上传文档到知识库"""
    kb = (
        db.query(KnowledgeBase)
        .filter(KnowledgeBase.id == kb_id, KnowledgeBase.user_id == user.id)
        .first()
    )
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")

    # 读取文件内容
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小超过限制")

    # 解析文本
    text = ""
    filename = file.filename or "unknown"
    if filename.endswith(".txt"):
        text = content.decode("utf-8")
    elif filename.endswith(".md"):
        text = content.decode("utf-8")
    else:
        raise HTTPException(status_code=400, detail="目前仅支持 .txt 和 .md 格式")

    # 文本切分与向量化
    chunks = rag_service.split_text(text)
    metadatas = [{"filename": filename, "chunk_index": i} for i in range(len(chunks))]
    rag_service.add_documents(kb_id, chunks, metadatas)

    # 保存文件记录
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    filepath = os.path.join(settings.UPLOAD_DIR, f"{kb_id}_{filename}")
    with open(filepath, "wb") as f:
        f.write(content)

    doc = Document(
        kb_id=kb_id,
        filename=filename,
        content=text[:1000],  # 只存前1000字符预览
        chunk_count=len(chunks),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/{kb_id}/documents", response_model=list[DocumentResponse])
def list_documents(
    kb_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取知识库下的文档列表"""
    kb = (
        db.query(KnowledgeBase)
        .filter(KnowledgeBase.id == kb_id, KnowledgeBase.user_id == user.id)
        .first()
    )
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")

    docs = db.query(Document).filter(Document.kb_id == kb_id).all()
    return docs
