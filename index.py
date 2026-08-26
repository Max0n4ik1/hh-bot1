import os
import json
from app.db.db import SessionLocal, engine, Base
from app.services.rag import get_response

# Создаём таблицы при первом запуске
Base.metadata.create_all(bind=engine)

def handler(event, context):
    try:
        # Входные данные могут быть в разных местах
        user_message = None
        
        # Сначала пробуем получить тело запроса
        body = event
        if 'body' in event:
            body = event['body']
        
        # Если body — строка, парсим JSON
        if isinstance(body, str):
            try:
                body = json.loads(body)
            except:
                body = {}
        
        # Пробуем извлечь текст из всех возможных мест
        if isinstance(body, dict):
            # Вариант 1: message.text
            if 'message' in body and isinstance(body['message'], dict):
                user_message = body['message'].get('text', '')
            # Вариант 2: text
            elif 'text' in body:
                user_message = body['text']
            # Вариант 3: question
            elif 'question' in body:
                user_message = body['question']
            # Вариант 4: request.message (для некоторых интеграций)
            elif 'request' in body and isinstance(body['request'], dict):
                user_message = body['request'].get('text', body['request'].get('question', ''))
        
        # Если ничего не нашли — выводим весь запрос для отладки
        if not user_message:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'response': {
                        'text': f"Я получил запрос, но не нашёл вопрос. Структура: {json.dumps(body, ensure_ascii=False)[:200]}",
                        'end_session': False
                    }
                }, ensure_ascii=False)
            }
        
        # Получаем ответ через RAG
        db = SessionLocal()
        try:
            result = get_response(db, user_message)
            answer = result['answer']
        finally:
            db.close()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'response': {
                    'text': answer,
                    'end_session': False
                }
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'response': {
                    'text': f'Ошибка: {str(e)}',
                    'end_session': True
                }
            }, ensure_ascii=False)
        }