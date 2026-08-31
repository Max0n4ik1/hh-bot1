from sqlalchemy.orm import Session
from app.db import models


# ========== CRUD для Category ==========

def create_category(db: Session, title: str):
    db_category = models.Category(title=title)
    db.add(db_category)
    db.commit()
    return db_category


def get_categories(db: Session):
    return db.query(models.Category).all()


def get_category_by_id(db: Session, category_id: int):
    return db.query(models.Category).filter(models.Category.id == category_id).first()


def get_category_by_title(db: Session, title: str):
    return db.query(models.Category).filter(models.Category.title == title).first()


def update_category(db: Session, category_id: int, new_title: str):
    category = get_category_by_id(db, category_id)
    if category:
        category.title = new_title
        db.commit()
    return category


def delete_category(db: Session, category_id: int):
    category = get_category_by_id(db, category_id)
    if category:
        db.delete(category)
        db.commit()
    return category


# ========== CRUD для Book ==========

def create_book(db: Session, book_data):
    db_book = models.Book(
        title=book_data.title,
        description=book_data.description,
        price=book_data.price,
        url=book_data.url or "",
        category_id=book_data.category_id
    )
    db.add(db_book)
    db.commit()
    return db_book


def get_books(db: Session, category_id: int = None):
    query = db.query(models.Book)
    if category_id:
        query = query.filter(models.Book.category_id == category_id)
    return query.all()


def get_book_by_id(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()


def update_book(db: Session, book_id: int, book_data):
    book = get_book_by_id(db, book_id)
    if not book:
        return None
    update_data = book_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(book, key, value)
    db.commit()
    return book


def delete_book(db: Session, book_id: int):
    book = get_book_by_id(db, book_id)
    if book:
        db.delete(book)
        db.commit()
    return book


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


def get_dialogs_by_user(db: Session, user_id: int, limit: int = 10):
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
    user = models.User(
        user_id=user_id,
        name=name
    )
    db.add(user)
    db.commit()
    return user


def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.user_id == user_id).first()


def update_user_last_active(db: Session, user_id: str):
    user = get_user(db, user_id)
    if user:
        from datetime import datetime
        user.last_active = datetime.utcnow()
        db.commit()
    return user