from telegram import Update
from telegram.ext import ContextTypes

from src.decorators.adminOnly import admin_only


@admin_only
async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tokens = update.message.text.split(" ")
    if len(tokens) > 2:
        await context.bot.send_message(chat_id=tokens[1], text=" ".join(tokens[2:]))
        await update.message.chat.send_message("send!")
    else:
        await update.message.chat.send_message(f"need some more tokens({len(tokens)})")
