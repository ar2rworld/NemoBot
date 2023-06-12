from telegram import Update
from telegram.ext import ContextTypes

from src.handlers.room204 import osuzhdau
from src.handlers.stats import save_conversation
from src.utils.echo import echo


async def echo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await echo(update, context)

    save_conversation(context, update.message)

    await osuzhdau(update, context)

    bot_data = context.application.bot_data
    if update.message is None or update.message.from_user is None:
        msg = "Missing message or chat or from_user"
        raise ValueError(msg)
    try:
        user_id = update.message.from_user.id
        bot_data["echoHandlers"][user_id](update, context)
    except KeyError:
        pass
