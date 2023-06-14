## pyright: reportOptionalMemberAccess=false

import re

from telegram import Update
from telegram.ext import ContextTypes

from src.decorators.admin_only import admin_only
from src.errors.error_codes import MISSING_MESSAGE_OR_TEXT
from src.mongo.mongo_connection import add_to_collection


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.text is None:
        raise ValueError(MISSING_MESSAGE_OR_TEXT)
    echo_phrases = context.application.bot_data["echoPhrases"]
    for phrase in echo_phrases:
        try:
            pattern = phrase["phrase"].lower()
            reg = pattern.replace(" ", r"\s*")
            text = update.message.text.lower()
            out = re.match(r".*" + reg + r".*", text)
            if out:
                await update.message.chat.send_message(phrase["answer"])
        except ValueError as v:
            context.application.bot_data["errorLogger"].error(v)
        except KeyError as k:
            context.application.bot_data["errorLogger"].error(k)


@admin_only
async def add_echo_phrase(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.text is None:
        raise ValueError(MISSING_MESSAGE_OR_TEXT)
    message = update.message.text.replace("/addEchoPhrase ", "")
    if "|-|" in message:
        phrase, answer = message.split("|-|")
        obj = {"phrase": phrase.lower(), "answer": answer}
        context.application.bot_data["echoPhrases"].append(obj)
        result = add_to_collection(context, "echoPhrases", obj, upsert_key="phrase")
        await update.message.chat.send_message(f"Added {result.acknowledged}")
    else:
        await update.message.chat.send_message("'|-|' delimiter is missing")
