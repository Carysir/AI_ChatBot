"""应用配置"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # 应用配置
    APP_NAME: str = "智能聊天机器人"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./chatbot.db")

    # JWT 配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时

    # LLM 配置 - 默认使用智谱 GLM
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "zhipu")  # zhipu / openai / qwen
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "glm-4-flash")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "")

    # RAG 配置
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    TOP_K: int = int(os.getenv("TOP_K", "3"))
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "./vector_store")

    # 文件上传配置
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]


settings = Settings()
