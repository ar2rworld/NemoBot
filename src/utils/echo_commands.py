from telegram import Message
from telegram import Update
from telegram.ext import ContextTypes


async def my_telegram_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
    if update.message is None:
        msg = "Missing message"
        raise ValueError(msg)
    return await update.message.chat.send_message(str(update.message))
