from sqlalchemy.orm import Session
from app.db import models
from app.services.yandex import ask_yandex_gpt


def search_knowledge_base(db: Session, query: str, limit: int = 5) -> str:
    """
    Ищет в базе знаний фрагменты, релевантные запросу.
    Пока используем простой поиск по ключевым словам.
    (Позже можно добавить векторный поиск)
    """
    # Простой поиск по ключевым словам
    keywords = query.lower().split()
    
    results = db.query(models.KnowledgeBase).all()
    scored = []
    
    for item in results:
        score = 0
        content_lower = item.content.lower()
        for keyword in keywords:
            if keyword in content_lower:
                score += 1
        if score > 0:
            scored.append((score, item))
    
    # Сортируем по релевантности
    scored.sort(key=lambda x: x[0], reverse=True)
    
    # Берём топ результатов
    top_results = [item for _, item in scored[:limit]]
    
    if not top_results:
        return ""
    
    # Объединяем найденные фрагменты
    context = "\n\n---\n\n".join([item.content for item in top_results])
    return context


def get_response(db: Session, question: str) -> dict:
    """
    Основная функция RAG-пайплайна:
    1. Поиск в базе знаний
    2. Генерация ответа через YandexGPT
    """
    # Шаг 1: Поиск контекста
    context = search_knowledge_base(db, question)
    
    # Шаг 2: Генерация ответа
    if context:
        answer = ask_yandex_gpt(question, context)
    else:
        answer = "К сожалению, я не нашел информации по вашему вопросу в базе знаний. Попробуйте переформулировать вопрос или обратитесь к официальной документации: https://github.com/hhru/api"
    
    return {
        "answer": answer,
        "context": context if context else None,
        "has_context": bool(context)
    }