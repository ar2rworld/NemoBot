from telegram import Update
from telegram.ext import ContextTypes

from src.decorators.admin_only import admin_only
from src.errors.error_codes import MISSING_MESSAGE_OR_CHAT_TEXT


@admin_only
async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.chat is None or update.message.text is None:
        raise ValueError(MISSING_MESSAGE_OR_CHAT_TEXT)
    tokens = update.message.text.split(" ")
    if len(tokens) > 2:
        await context.bot.send_message(chat_id=tokens[1], text=" ".join(tokens[2:]))
        await update.message.chat.send_message("send!")
    else:
        await update.message.chat.send_message(f"need some more tokens({len(tokens)})")
