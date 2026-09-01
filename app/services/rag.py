import json
import numpy as np
from sqlalchemy.orm import Session
from app.db import models
from app.services.yandex import ask_yandex_gpt
from app.services.embedder import get_embedding


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def search_knowledge_base(db: Session, query: str, limit: int = 10, min_score: float = 0.3) -> tuple:
    query_embedding = get_embedding(query)
    items = db.query(models.KnowledgeBase).filter(
        models.KnowledgeBase.embedding.isnot(None)
    ).all()
    
    scored = []
    for item in items:
        try:
            item_embedding = json.loads(item.embedding)
            score = cosine_similarity(query_embedding, item_embedding)
            scored.append((score, item))
        except:
            continue
    
    scored.sort(key=lambda x: x[0], reverse=True)
    
    top_results = []
    for score, item in scored:
        if score >= min_score:
            top_results.append((score, item))
        if len(top_results) >= limit:
            break
    
    if not top_results:
        return "", []
    
    seen_urls = set()
    unique_sources = []
    for score, item in top_results:
        if item.source_url not in seen_urls:
            seen_urls.add(item.source_url)
            unique_sources.append((score, item))
    
    context_parts = []
    sources = []
    for score, item in unique_sources[:5]:
        context_parts.append(item.content)
        title = item.title.replace('_', ' ').replace('-', ' ').title()
        sources.append(f"• **{title}** — [читать]({item.source_url}) (релевантность: {score:.2f})")
    
    context = "\n\n---\n\n".join(context_parts)
    return context, sources


def get_response(db: Session, question: str, history: list = None) -> dict:
    context, sources = search_knowledge_base(db, question)
    
    # Формируем контекст с учётом истории
    if context:
        if history:
            history_text = "\n".join([f"Пользователь: {h.question}\nБот: {h.answer}" for h in history])
            full_context = f"История диалога:\n{history_text}\n\nТекущий вопрос: {question}\n\nДокументация:\n{context}"
        else:
            full_context = f"Вопрос: {question}\n\nДокументация:\n{context}"
        
        answer = ask_yandex_gpt(question, full_context)
        
        if sources:
            top_sources = sources[:3]
            sources_text = "\n\n📚 **Источники:**\n" + "\n".join(top_sources)
            sources_text += "\n\n🔗 [Полная документация HH.ru](https://github.com/hhru/api)"
            answer = answer + sources_text
    else:
        answer = (
            "🤔 К сожалению, я не нашёл информации по вашему вопросу в базе знаний.\n\n"
            "💡 Попробуйте переформулировать вопрос или обратитесь к официальной документации:\n"
            "🔗 https://github.com/hhru/api"
        )
    
    return {
        "answer": answer,
        "sources": sources,
        "has_context": bool(context)
    }