from telegram import Update
from telegram.ext import ContextTypes

from src.errors.error_codes import MISSING_MESSAGE_OR_FROM_USER
from src.handlers.context_executors import save_conversation
from src.handlers.room204 import osuzhdau
from src.utils.echo import echo


async def echo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await echo(update, context)

    if update.message:
        save_conversation(context, update.message)

    await osuzhdau(update, context)

    bot_data = context.application.bot_data
    if update.message is None or update.message.from_user is None:
        raise ValueError(MISSING_MESSAGE_OR_FROM_USER)
    try:
        user_id = update.message.from_user.id
        bot_data["echoHandlers"][user_id](update, context)
    except KeyError:
        pass
