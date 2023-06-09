from telegram import Update
from telegram.ext import ContextTypes


async def my_telegram_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is not None:
        await update.message.chat.send_message(str(update.message))
