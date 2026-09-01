import os
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from app.services.rag import get_response
from app.services.kb_loader import load_knowledge_base
from app.db.db import SessionLocal
from app.db.crud import save_dialog, get_dialogs_by_user, create_user, get_user, update_user_last_active

# ========== Telegram Token ==========
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# ========== Администраторы ==========
ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]


# ========== Команда /start ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот-помощник по API HeadHunter (HH.ru).\n"
        "Задай мне вопрос, и я постараюсь найти ответ в документации."
    )


# ========== Обработка сообщений ==========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = update.effective_user.id
    print(f"📩 Получен вопрос: {user_message}")
    
    db = SessionLocal()
    try:
        # Создаём пользователя, если его нет
        if not get_user(db, str(user_id)):
            create_user(db, str(user_id), update.effective_user.full_name)
        else:
            update_user_last_active(db, str(user_id))
        
        # Получаем историю диалогов (последние 3)
        history = get_dialogs_by_user(db, user_id, limit=3)
        
        # Получаем ответ от RAG
        result = get_response(db, user_message, history)
        answer = result["answer"]
        
        # Обрезаем сообщение до лимита Telegram (4096 символов)
        if len(answer) > 4096:
            answer = answer[:4093] + "..."
        
        # Сохраняем диалог в БД
        save_dialog(db, user_id, user_message, answer)
        
        print(f"✅ Ответ отправлен")
        await update.message.reply_text(answer, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text("❌ Произошла ошибка. Попробуйте позже.")
    finally:
        db.close()


# ========== Команда /update_kb (только для админов) ==========
async def update_kb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверяем, админ ли пользователь
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ У вас нет прав на эту команду.")
        return
    
    await update.message.reply_text("🔄 Начинаю обновление базы знаний...")
    
    db = SessionLocal()
    try:
        count = load_knowledge_base(db)
        await update.message.reply_text(f"✅ База знаний обновлена! Добавлено {count} новых фрагментов.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")
    finally:
        db.close()


# ========== Запуск бота ==========
if __name__ == "__main__":
    if not TELEGRAM_TOKEN:
        print("❌ Ошибка: TELEGRAM_TOKEN не задан в .env")
        exit(1)
    
    # Простой запуск без прокси
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Регистрируем команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("update_kb", update_kb))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Бот запущен и готов к работе!")
    app.run_polling()