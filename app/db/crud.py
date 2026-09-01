from sqlalchemy.orm import Session
from app.db import models
from datetime import datetime


# ========== CRUD для Dialog ==========

def save_dialog(db: Session, user_id: int, question: str, answer: str):
    """Сохраняет диалог в базу данных"""
    dialog = models.Dialog(
        user_id=str(user_id),
        question=question,
        answer=answer
    )
    db.add(dialog)
    db.commit()
    return dialog


def get_dialogs_by_user(db: Session, user_id: int, limit: int = 5):
    """Получает последние диалоги пользователя"""
    return db.query(models.Dialog).filter(
        models.Dialog.user_id == str(user_id)
    ).order_by(models.Dialog.created_at.desc()).limit(limit).all()


def get_all_dialogs(db: Session, limit: int = 50):
    """Получает последние диалоги всех пользователей"""
    return db.query(models.Dialog).order_by(
        models.Dialog.created_at.desc()
    ).limit(limit).all()


# ========== CRUD для User ==========

def create_user(db: Session, user_id: str, name: str = None):
    """Создаёт нового пользователя"""
    user = models.User(
        user_id=user_id,
        name=name
    )
    db.add(user)
    db.commit()
    return user


def get_user(db: Session, user_id: str):
    """Получает пользователя по ID"""
    return db.query(models.User).filter(models.User.user_id == user_id).first()


def update_user_last_active(db: Session, user_id: str):
    """Обновляет время последней активности пользователя"""
    user = get_user(db, user_id)
    if user:
        user.last_active = datetime.utcnow()
        db.commit()
    return user