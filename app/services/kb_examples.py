from app.db.db import SessionLocal
from app.db.models import KnowledgeBase

def add_examples():
    db = SessionLocal()
    
    examples = [
        {
            "title": "Как получить список вакансий",
            "content": """
            Для получения списка вакансий используйте эндпоинт:

            GET /vacancies

            Параметры:
            - text (string) — поисковый запрос
            - area (int) — ID региона
            - salary (int) — зарплата
            - experience (string) — опыт работы

            Пример:
            GET /vacancies?text=Python&area=1

            Для получения вакансий конкретного работодателя:
            GET /employers/{employer_id}/vacancies

            Где {employer_id} — ID работодателя.
            """,
            "source_url": "https://github.com/hhru/api/blob/master/docs/vacancies.md",
            "category": "Вакансии"
        },
        {
            "title": "Как получить список вакансий работодателя",
            "content": """
            Для получения списка вакансий работодателя используйте эндпоинт:

            GET /employers/{employer_id}/vacancies

            Параметры:
            - page (int) — номер страницы
            - per_page (int) — количество на странице

            Пример:
            GET /employers/12345/vacancies?page=1&per_page=20

            Требуется авторизация с правами работодателя.
            """,
            "source_url": "https://github.com/hhru/api/blob/master/docs/employer_vacancies.md",
            "category": "Работодатели"
        }
    ]
    
    for ex in examples:
        # Проверяем, есть ли уже такой фрагмент
        existing = db.query(KnowledgeBase).filter(
            KnowledgeBase.title == ex["title"]
        ).first()
        
        if not existing:
            # Сохраняем без эмбеддинга (он будет сгенерирован при загрузке)
            kb = KnowledgeBase(
                title=ex["title"],
                content=ex["content"],
                source_url=ex["source_url"],
                category=ex["category"]
            )
            db.add(kb)
    
    db.commit()
    print("✅ Примеры добавлены в базу знаний")
    db.close()

if __name__ == "__main__":
    add_examples()