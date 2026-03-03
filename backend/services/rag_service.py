"""RAG 知识库检索服务"""
import json
import os
import re
from typing import Optional

from backend.config import settings


class RAGService:
    """RAG 检索增强生成服务"""

    def __init__(self):
        self._vectorstore = {}  # kb_id -> FAISS index
        self._embeddings = None
        self._init_embeddings()

    def _init_embeddings(self):
        """初始化 Embedding 模型（使用 HuggingFace 本地模型）"""
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings

            self._embeddings = HuggingFaceEmbeddings(
                model_name="shibing624/text2vec-base-chinese",
                model_kwargs={"device": "cpu"},
            )
        except Exception:
            # 回退到简单的 TF-IDF 方案
            self._embeddings = None

    def split_text(self, text: str) -> list[str]:
        """文本切分"""
        chunk_size = settings.CHUNK_SIZE
        chunk_overlap = settings.CHUNK_OVERLAP

        # 按段落和句子切分
        paragraphs = re.split(r"\n\s*\n", text)
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            if len(current_chunk) + len(para) <= chunk_size:
                current_chunk += "\n" + para if current_chunk else para
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                # 保留重叠部分
                if chunk_overlap > 0 and current_chunk:
                    overlap_text = current_chunk[-chunk_overlap:]
                    current_chunk = overlap_text + "\n" + para
                else:
                    current_chunk = para

        if current_chunk:
            chunks.append(current_chunk)

        # 如果没有段落分隔，按固定长度切分
        if not chunks:
            for i in range(0, len(text), chunk_size - chunk_overlap):
                chunk = text[i : i + chunk_size]
                if chunk.strip():
                    chunks.append(chunk.strip())

        return chunks

    def add_documents(self, kb_id: int, texts: list[str], metadatas: list[dict] = None):
        """将文档添加到向量库"""
        if not texts:
            return

        store_path = os.path.join(settings.VECTOR_DB_PATH, str(kb_id))
        os.makedirs(store_path, exist_ok=True)

        if self._embeddings:
            from langchain_community.vectorstores import FAISS

            if kb_id in self._vectorstore:
                self._vectorstore[kb_id].add_texts(texts, metadatas=metadatas)
            else:
                self._vectorstore[kb_id] = FAISS.from_texts(
                    texts, self._embeddings, metadatas=metadatas
                )
            # 持久化保存
            self._vectorstore[kb_id].save_local(store_path)
        else:
            # 简单的关键词存储方案（回退）
            chunks_file = os.path.join(store_path, "chunks.json")
            existing = []
            if os.path.exists(chunks_file):
                with open(chunks_file, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            for i, text in enumerate(texts):
                meta = metadatas[i] if metadatas and i < len(metadatas) else {}
                existing.append({"text": text, "metadata": meta})
            with open(chunks_file, "w", encoding="utf-8") as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)

    def search(self, kb_id: int, query: str, top_k: int = None) -> list[dict]:
        """检索相似文档片段"""
        if top_k is None:
            top_k = settings.TOP_K

        store_path = os.path.join(settings.VECTOR_DB_PATH, str(kb_id))

        if self._embeddings:
            from langchain_community.vectorstores import FAISS

            if kb_id not in self._vectorstore:
                if os.path.exists(store_path):
                    try:
                        self._vectorstore[kb_id] = FAISS.load_local(
                            store_path,
                            self._embeddings,
                            allow_dangerous_deserialization=True,
                        )
                    except Exception:
                        return []
                else:
                    return []

            results = self._vectorstore[kb_id].similarity_search_with_score(query, k=top_k)
            return [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score),
                }
                for doc, score in results
            ]
        else:
            # 简单关键词匹配回退方案
            return self._keyword_search(store_path, query, top_k)

    def _keyword_search(self, store_path: str, query: str, top_k: int) -> list[dict]:
        """基于关键词的简单检索（回退方案）"""
        chunks_file = os.path.join(store_path, "chunks.json")
        if not os.path.exists(chunks_file):
            return []

        with open(chunks_file, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        query_chars = set(query)
        scored = []
        for chunk in chunks:
            text = chunk["text"]
            # 简单的字符重叠率计算
            text_chars = set(text)
            overlap = len(query_chars & text_chars)
            score = overlap / max(len(query_chars | text_chars), 1)
            scored.append({"content": text, "metadata": chunk.get("metadata", {}), "score": score})

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def delete_kb(self, kb_id: int):
        """删除知识库向量数据"""
        import shutil

        store_path = os.path.join(settings.VECTOR_DB_PATH, str(kb_id))
        if os.path.exists(store_path):
            shutil.rmtree(store_path)
        self._vectorstore.pop(kb_id, None)


# 全局实例
rag_service = RAGService()
