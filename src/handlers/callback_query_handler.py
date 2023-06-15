from collections.abc import Coroutine
from typing import Any

from telegram import Update
from telegram.ext import ContextTypes

from src.errors.error_codes import MISSING_CALLBACK_QUERY_OR_DATA


async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Coroutine[Any, Any, Any]:
    if update.callback_query is None or update.callback_query.data is None:
        raise ValueError(MISSING_CALLBACK_QUERY_OR_DATA)
    func = context.application.bot_data["callbackQueryHandlers"][update.callback_query.data]
    if not func:
        msg = f'Callback query handler: "{update.callback_query.data}" not found'
        raise Exception(msg)
    return await func(update, context)
