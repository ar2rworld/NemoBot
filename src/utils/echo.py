import re

from telegram import Update
from telegram.ext import ContextTypes

from src.decorators.adminOnly import adminOnly
from src.mongo.mongo_connection import add_to_collection


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    echoPhrases = context.application.bot_data["echoPhrases"]
    for phrase in echoPhrases:
        try:
            pattern = phrase["phrase"].lower()
            reg = pattern.replace(" ", r"\s*")
            out = re.match(r".*" + reg + r".*", update.message.text.lower())
            if out:
                await update.message.chat.send_message(phrase["answer"])
        except Exception as e:
            print(e)


@adminOnly
async def addEchoPhrase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.replace("/addEchoPhrase ", "")
    if "|-|" in message:
        phrase, answer = message.split("|-|")
        obj = {"phrase": phrase.lower(), "answer": answer}
        context.application.bot_data["echoPhrases"].append(obj)
        result = add_to_collection(context, "echoPhrases", obj, upsert_key="phrase")
        await update.message.chat.send_message(f"Added {result.acknowledged}")
    else:
        await update.message.chat.send_message("'|-|' delimiter is missing")
