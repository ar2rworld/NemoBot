from telegram import Update
from telegram.ext import ContextTypes


def admin_only(func):
    async def inner(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message is None or update.message.chat is None or update.message.from_user is None:
            raise ValueError("Missing message or chat or from_user")
        user_id = str(update.message.from_user.id)
        bot_data = context.application.bot_data
        if user_id == bot_data["adminId"]:
            return await func(update, context)
        else:
            db = context.application.bot_data["db"]
            user = db.authorizedUsers.find_one({"tg_id": user_id})
            func_name = func.__name__
            if user and func_name in user["authorizedCommands"]:
                return await func(update, context)
            else:
                await update.message.chat.send_message("you not authorized to use this command")

    return inner
