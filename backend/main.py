"""FastAPI 应用入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import init_db
from backend.routers import chat_router, kb_router, user_router

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(user_router.router)
app.include_router(chat_router.router)
app.include_router(kb_router.router)


@app.on_event("startup")
def startup():
    """应用启动时初始化数据库"""
    init_db()


@app.get("/")
def root():
    return {"message": "智能聊天机器人 API", "version": settings.APP_VERSION}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
