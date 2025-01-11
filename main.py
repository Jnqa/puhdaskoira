from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv
import os
import re
import asyncio
from datetime import datetime

# Загрузка переменных из .env
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_CHATS = list(map(int, os.getenv("ALLOWED_CHATS").split(',')))
ADMINS = list(map(int, os.getenv("ADMINS").split(',')))
CHAT_ADMIN_MAP = dict(zip(ALLOWED_CHATS, ADMINS))
print("🐕 woof!")

# Настройка бота
application = Application.builder().token(TOKEN).build()

spam_patterns = [
    r"(?:срочно|халтура|платим|депозит|казино|пассивный заработок|удалённая деятельность|гибкий график|достойный доход)",
    r"\d+\s?(тысяч|к|р|руб)",
    r"[CcСс][PpРр][OoОо0][Чч][HnНн]"
]

async def log_event(context: CallbackContext, chat_id, user, message, joined_hours_ago, spam_detected):
    log_mode = context.bot_data.get("log_mode", "logs_off")
    if log_mode == "logs_off":
        return

    admin_id = CHAT_ADMIN_MAP.get(chat_id)
    if not admin_id:
        return

    status = "Ban [⚠️]" if spam_detected else "Info"
    markers_status = "да" if spam_detected else "нет"
    time_status = f"{int(joined_hours_ago)}h" if joined_hours_ago != float('inf') else "unknown"

    log_text = (
        f"🪵 ⟶ {status}\n"
        f"☑️ ⟶ {markers_status} | 🕓<48 ⟶ {'да' if joined_hours_ago <= 48 else 'нет'} ({time_status})\n"
        f"🗨️ ⟶ {user}: {message}"
    )
    try:
        await context.bot.send_message(admin_id, log_text)
    except Exception as e:
        print(f"Ошибка логирования: {e}")

async def get_joined_hours_ago(context: CallbackContext, chat_id, user_id):
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return 0
    except Exception as e:
        print(f"Ошибка получения данных о члене чата: {e}")
    return float('inf')

async def is_spam(update: Update, context: CallbackContext):
    message = update.message
    if message.chat.id > 0:
        return any(re.search(pattern, message.text, re.IGNORECASE) for pattern in spam_patterns)

    if message.chat.id in ALLOWED_CHATS:
        joined_hours_ago = await get_joined_hours_ago(context, message.chat.id, message.from_user.id)
        spam_detected = any(re.search(pattern, message.text, re.IGNORECASE) for pattern in spam_patterns)
        await log_event(context, message.chat.id, message.from_user.full_name, message.text, joined_hours_ago, spam_detected)
        return spam_detected and joined_hours_ago <= 48
    return False

async def delete_and_ban(update: Update, context: CallbackContext):
    message = update.message
    if message.chat.id < 0 and await is_spam(update, context):
        reply_message = await message.reply_text("🐕!")
        await asyncio.sleep(3)
        try:
            await message.delete()
            await context.bot.ban_chat_member(message.chat.id, message.from_user.id)
            await reply_message.delete()
        except Exception as e:
            print(f"Ошибка удаления или бана: {e}")

async def set_logs_off(update: Update, context: CallbackContext):
    if update.message.from_user.id in ADMINS:
        context.bot_data["log_mode"] = "logs_off"
        await update.message.reply_text("Логи отключены.")

async def set_logs_ban(update: Update, context: CallbackContext):
    if update.message.from_user.id in ADMINS:
        context.bot_data["log_mode"] = "logs_ban"
        await update.message.reply_text("Логи только при бане.")

async def set_logs_all(update: Update, context: CallbackContext):
    if update.message.from_user.id in ADMINS:
        context.bot_data["log_mode"] = "logs_all"
        await update.message.reply_text("Логи всех сообщений включены.")

async def get_id(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id
    await update.message.reply_text(f"ID чата: {chat_id}\nВаш ID: {user_id}")
    try:
        await update.message.delete()
    except Exception as e:
        print(f"Ошибка удаления или бана: {e}")

async def woof_message(update: Update, context: CallbackContext):
    reply_message = await update.message.reply_text("🐕 woof!")
    await asyncio.sleep(3)
    try:
        await update.message.delete()
        await reply_message.delete()
    except Exception as e:
        print(f"Ошибка удаления или бана: {e}")

async def start_message(update: Update, context: CallbackContext):
    await update.message.reply_text("Готов заняться уборкой!")
    await update.message.delete()

async def help_message(update: Update, context: CallbackContext):
    help_text = (
        "Доступные команды:\n"
        "/logs_off - отключить логи (defaut)\n"
        "/logs_ban - логи только при бане\n"
        "/logs_all - логи всех сообщений\n"
        "/getid - получить id чата\n"
        "/woof - проверить связь с ботом"
    )
    try:
        await update.message.delete()
    except Exception as e:
        print(f"Ошибка удаления или бана: {e}")
    await update.message.reply_text(help_text)

application.add_handler(CommandHandler("logs_off", set_logs_off))
application.add_handler(CommandHandler("logs_ban", set_logs_ban))
application.add_handler(CommandHandler("logs_all", set_logs_all))
application.add_handler(CommandHandler("start", start_message))
application.add_handler(CommandHandler("getid", get_id))
application.add_handler(CommandHandler("woof", woof_message))
application.add_handler(CommandHandler("help", help_message))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, delete_and_ban))

if __name__ == "__main__":
    application.bot_data["log_mode"] = "logs_off"
    application.run_polling()
