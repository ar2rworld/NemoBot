from collections.abc import Callable
from collections.abc import Coroutine
from typing import Any

from telegram import Update
from telegram.ext import ContextTypes


def admin_only(func: Callable) -> Callable[...]:
    async def inner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Coroutine[Any, Any, Any]:
        if update.message is None or update.message.chat is None or update.message.from_user is None:
            msg = "Missing message or chat or from_user"
            raise ValueError(msg)
        user_id = str(update.message.from_user.id)
        bot_data = context.application.bot_data
        if user_id == bot_data["adminId"]:
            return await func(update, context)
        db = context.application.bot_data["db"]
        user = db.authorizedUsers.find_one({"tg_id": user_id})
        func_name = func.__name__
        if user and func_name in user["authorizedCommands"]:
            return await func(update, context)
        return await update.message.chat.send_message("you not authorized to use this command")

    return inner
