from telegram import Update
from telegram.ext import ContextTypes

from src.mongo.mongo_connection import add_to_collection


async def addAlivePhrases(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.replace("/addAlivePhrases ", "")
    delimiter = "|,|"
    n = 0
    if delimiter in message:
        phrases = message.split(delimiter)
        for phrase in phrases:
            if phrase:
                obj = {"phrase": phrase}
                context.application.bot_data["alivePhrases"].append(obj)
                result = add_to_collection(context, "alivePhrases", obj)
                if result.acknowledged:
                    n += 1
    else:
        if message:
            obj = {"phrase": message}
            context.application.bot_data["alivePhrases"].append(obj)
            result = add_to_collection(context, "alivePhrases", obj)
            if result.acknowledged:
                n += 1
    await update.message.chat.send_message(f"Phrases added: {n}")
