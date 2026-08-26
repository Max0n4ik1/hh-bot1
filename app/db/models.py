from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.db import Base


class KnowledgeBase(Base):
    """Таблица для хранения фрагментов документации HH.ru"""
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)          # Заголовок раздела
    content = Column(Text)                      # Текст фрагмента
    source_url = Column(String)                 # Ссылка на источник
    category = Column(String, index=True)       # Категория (вакансии, резюме и т.д.)
    embedding = Column(JSON, nullable=True)     # Векторное представление (для поиска)
    created_at = Column(DateTime, default=datetime.utcnow)


class Dialog(Base):
    """Таблица для хранения истории диалогов"""
    __tablename__ = "dialogs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)        # ID пользователя в MAX
    question = Column(Text)                     # Вопрос пользователя
    answer = Column(Text)                       # Ответ бота
    source = Column(Text, nullable=True)        # Источник информации
    created_at = Column(DateTime, default=datetime.utcnow)


class User(Base):
    """Таблица для хранения информации о пользователях (опционально)"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)  # ID пользователя в MAX
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)