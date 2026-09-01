import os
import requests
import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.db.models import KnowledgeBase
from app.services.embedder import get_embedding

# URL для скачивания документации HH.ru
HH_DOCS_URL = "https://api.github.com/repos/hhru/api/contents/docs"


def download_documentation():
    """Скачивает документацию HH.ru из GitHub"""
    response = requests.get(HH_DOCS_URL)
    if response.status_code != 200:
        print(f"❌ Ошибка загрузки: {response.status_code}")
        return []
    
    files = response.json()
    docs = []
    
    for file in files:
        if file['name'].endswith('.md'):
            # Скачиваем содержимое файла
            content_response = requests.get(file['download_url'])
            if content_response.status_code == 200:
                docs.append({
                    'title': file['name'].replace('.md', ''),
                    'content': content_response.text,
                    'source_url': file['html_url'],
                    'category': file['name'].split('.')[0]  # Простая категоризация
                })
                print(f"✅ Загружен: {file['name']}")
    
    return docs


def save_to_database(db: Session, docs: list):
    """Сохраняет документацию в базу данных с эмбеддингами (с обновлением)"""
    count = 0
    for doc in docs:
        # Находим все старые фрагменты этого документа
        old_items = db.query(KnowledgeBase).filter(
            KnowledgeBase.source_url == doc['source_url']
        ).all()
        
        # Удаляем старые фрагменты
        for item in old_items:
            db.delete(item)
            count += 1  # считаем удалённые как обновлённые
        
        # Добавляем новые фрагменты
        fragments = split_by_headers(doc['content'])
        for fragment in fragments:
            embedding = get_embedding(fragment)
            kb_entry = KnowledgeBase(
                title=doc['title'],
                content=fragment,
                source_url=doc['source_url'],
                category=doc['category'],
                embedding=json.dumps(embedding)
            )
            db.add(kb_entry)
            count += 1
        
        db.commit()
    
    print(f"✅ Обновлено {count} фрагментов в базе знаний")
    return count

def split_by_headers(content: str) -> list:
    """Разбивает документ на фрагменты по заголовкам"""
    fragments = []
    lines = content.split('\n')
    current = []
    
    for line in lines:
        if line.startswith('##') or line.startswith('###'):
            if current:
                fragments.append('\n'.join(current))
                current = []
        current.append(line)
    
    if current:
        fragments.append('\n'.join(current))
    
    return fragments if fragments else [content]


def load_knowledge_base(db: Session):
    """Основная функция для загрузки базы знаний"""
    print("📥 Загрузка документации HH.ru...")
    docs = download_documentation()
    
    if not docs:
        print("❌ Не удалось загрузить документацию")
        return 0
    
    print(f"📚 Загружено {len(docs)} файлов")
    count = save_to_database(db, docs)
    return count