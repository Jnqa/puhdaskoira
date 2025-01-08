from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv
import os
import re
from datetime import datetime, timedelta

# Загрузка переменных из .env
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_CHATS = list(map(int, os.getenv("ALLOWED_CHATS").split(',')))
ADMINS = list(map(int, os.getenv("ADMINS").split(',')))
CHAT_ADMIN_MAP = dict(zip(ALLOWED_CHATS, ADMINS))

# Настройка бота
application = Application.builder().token(TOKEN).build()

spam_patterns = [
    r"(?:срочно|халтура|платим|сразу на руки|депозит|казино|пассивный заработок|удалённая деятельность|гибкий график|достойный доход)",
    r"\d+\s?(тысяч|к|р|руб)",
    r"[CcСс][PpРр][OoОо0][Чч][HnНн]"
]

logging_enabled = True

# Логирование спама привязанному админу чата
async def log_spam(chat_id, user, message):
    if logging_enabled and chat_id in CHAT_ADMIN_MAP:
        admin_id = CHAT_ADMIN_MAP[chat_id]
        log_text = f"{datetime.now()} - {user}: {message}"
        try:
            await application.bot.send_message(admin_id, f"⚠️ СПАМ: {log_text}")
        except Exception as e:
            print(f"Ошибка отправки лога админу {admin_id}: {e}")

# Проверка нового участника
async def is_new_member(chat_id, user_id):
    member = await application.bot.get_chat_member(chat_id, user_id)
    if member.status in ['member', 'restricted'] and member.joined_date:
        if datetime.now() - member.joined_date < timedelta(hours=48):
            return True
    return False

# Проверка спама
async def is_spam(update: Update):
    message = update.message
    if message.chat.id in ALLOWED_CHATS and await is_new_member(message.chat.id, message.from_user.id):
        for pattern in spam_patterns:
            if re.search(pattern, message.text, re.IGNORECASE):
                await log_spam(message.chat.id, message.from_user.full_name, message.text)
                return True
    return False

# Обработка сообщений с возможным спамом
async def delete_and_ban(update: Update, context: CallbackContext):
    if await is_spam(update):
        message = update.message
        reply_message = await update.message.reply_text("🐕!")
        await asyncio.sleep(3)
        await message.delete()
        await application.bot.ban_chat_member(message.chat.id, message.from_user.id)
        await reply_message.delete()

# Включение/выключение логов (только для привязанного админа)
async def toggle_logs(update: Update, context: CallbackContext):
    global logging_enabled
    if update.message.from_user.id in ADMINS:
        logging_enabled = not logging_enabled
        await update.message.reply_text(f"Логи {'включены' if logging_enabled else 'отключены'}.")
    else:
        await update.message.reply_text("У вас нет прав для этой команды.")

# Обработка пересылок для получения ID чата и ID пользователя
async def forward_info(update: Update, context: CallbackContext):
    if update.message.forward_from_chat:
        user_id = update.message.from_user.id
        chat_id = update.message.forward_from_chat.id
        await update.message.reply_text(f"ID чата: {chat_id}\nВаш ID: {user_id}")

# Команда для тестового удаления и блокировки
async def test_delete_and_ban(update: Update, context: CallbackContext):
    # Имитируем удаление и логирование
    if update.message.chat.id in ALLOWED_CHATS:
        message = update.message
        await message.delete()
        await log_spam(message.chat.id, message.from_user.full_name, message.text)
        reply_message = await update.message.reply_text("Сообщение удалено и лог отправлен.")
        await asyncio.sleep(3)
        await reply_message.delete()

# Команда для получения ID чата и отправителя
async def get_id(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id
    await update.message.reply_text(f"ID чата: {chat_id}\nВаш ID: {user_id}")
    await update.message.delete()  # Удаление команды после ответа

# Команда /start
async def start_message(update: Update, context: CallbackContext):
    await update.message.reply_text("Готов заняться уборкой!(v1)")
    await update.message.delete()  # Удаление команды /start

# Добавление хендлеров
application.add_handler(CommandHandler("start", start_message))
application.add_handler(CommandHandler("toggle_logs", toggle_logs))
application.add_handler(CommandHandler("test_delete_and_ban", test_delete_and_ban))  # Тестовая команда
application.add_handler(CommandHandler("getid", get_id))  # Команда для получения ID
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, delete_and_ban))  # Обрабатываем текстовые сообщения
application.add_handler(MessageHandler(filters.FORWARDED, forward_info))  # Обрабатываем пересланные сообщения

if __name__ == "__main__":
    application.run_polling()
