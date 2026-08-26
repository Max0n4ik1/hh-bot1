from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import webhook
from app.db.db import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Действия при запуске
    Base.metadata.create_all(bind=engine)
    print("🚀 Сервер запущен")
    print("📚 Документация API: http://127.0.0.1:8000/docs")
    yield
    # Действия при остановке
    print("🛑 Сервер остановлен")


app = FastAPI(
    title="HH API Assistant",
    description="Чат-бот для вопросов по API HeadHunter (RAG + YandexGPT)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(webhook.router)


@app.get("/")
async def root():
    return {
        "message": "HH API Assistant Bot",
        "webhook": "/webhook",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {"status": "ok", "service": "HH API Assistant"}