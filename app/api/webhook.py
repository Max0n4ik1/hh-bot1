from fastapi import APIRouter, HTTPException, Request
from app.db.db import SessionLocal
from app.services.rag import get_response

router = APIRouter(prefix="/webhook", tags=["Webhook"])


@router.post("/")
async def handle_webhook(request: Request):
    """
    Эндпоинт для приёма запросов от Yandex Assistant (MAX).
    """
    try:
        # Получаем данные от Yandex Assistant
        data = await request.json()
        
        # Извлекаем вопрос пользователя
        # Формат запроса от MAX может отличаться, адаптируем
        user_message = data.get("message", {}).get("text", "")
        user_id = data.get("message", {}).get("from", {}).get("id", "unknown")
        
        if not user_message:
            return {"response": {"text": "Пожалуйста, напишите ваш вопрос."}}
        
        # Получаем ответ через RAG
        db = SessionLocal()
        try:
            result = get_response(db, user_message)
            answer = result["answer"]
        finally:
            db.close()
        
        # Формируем ответ для Yandex Assistant
        return {
            "response": {
                "text": answer,
                "end_session": False  # Продолжаем диалог
            }
        }
        
    except Exception as e:
        print(f"❌ Ошибка в webhook: {e}")
        return {
            "response": {
                "text": "Извините, произошла ошибка. Попробуйте позже.",
                "end_session": True
            }
        }


@router.get("/")
async def webhook_info():
    """
    Проверка работоспособности вебхука.
    """
    return {
        "status": "ok",
        "message": "Webhook для Yandex Assistant (MAX) работает!"
    }