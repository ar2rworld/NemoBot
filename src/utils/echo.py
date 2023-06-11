## pyright: reportOptionalMemberAccess=false

import re

from telegram import Update
from telegram.ext import ContextTypes

from src.decorators.adminOnly import admin_only
from src.mongo.mongo_connection import add_to_collection


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.message.text is None:
        raise ValueError("Missing message or text")
    echo_phrases = context.application.bot_data["echoPhrases"]
    for phrase in echo_phrases:
        try:
            pattern = phrase["phrase"].lower()
            reg = pattern.replace(" ", r"\s*")
            text = update.message.text.lower()
            out = re.match(r".*" + reg + r".*", text)
            if out:
                await update.message.chat.send_message(phrase["answer"])
        except Exception as e:
            context.application.bot_data["errorLogger"].error(e)


@admin_only
async def add_echo_phrase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.message.text is None:
        raise ValueError("Missing message or text")
    message = update.message.text.replace("/addEchoPhrase ", "")
    if "|-|" in message:
        phrase, answer = message.split("|-|")
        obj = {"phrase": phrase.lower(), "answer": answer}
        context.application.bot_data["echoPhrases"].append(obj)
        result = add_to_collection(context, "echoPhrases", obj, upsert_key="phrase")
        await update.message.chat.send_message(f"Added {result.acknowledged}")
    else:
        await update.message.chat.send_message("'|-|' delimiter is missing")
