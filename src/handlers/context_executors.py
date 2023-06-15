import subprocess
from os import getenv

from pymongo.database import Database
from redis import Redis
from telegram import KeyboardButton
from telegram import Message
from telegram import ReplyKeyboardMarkup
from telegram.ext import Application
from telegram.ext import ContextTypes

from src.utils.other import pick_random_from_list


async def send_alive_message(context: ContextTypes.DEFAULT_TYPE) -> None:
    app: Application = context.application
    # send alive messages
    await app.bot.send_message(
        app.bot_data["tg_my_id"],
        "hello comrade!",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("/help")], [KeyboardButton("/requestAccess")]]),
    )
    if not getenv("DEBUG"):
        commits = subprocess.check_output(["git", "log"]).decode("utf-8")
        last_commit = commits[commits.find("Author", 1) : commits.find("commit", 1)].replace("\n", "")
        phrase = pick_random_from_list(app.bot_data["alivePhrases"])["phrase"]
        channel_post = f"{last_commit}\n{phrase}"
        await app.bot.send_message(app.bot_data["botChannel"], channel_post)
        await app.bot.send_message(app.bot_data["botGroup"], phrase)


def save_conversation(context: ContextTypes.DEFAULT_TYPE, message: Message) -> None:
    r: Redis = context.application.bot_data["r"]
    db: Database = context.application.bot_data["db"]
    # check if chat id is in redis
    chat_ids = r.lrange("chat_ids", 0, -1)
    chat_id = message.chat.id
    chat_title = message.chat.title
    username = message.chat.username
    chat_name = str(chat_title or username).replace("'", "")

    if str(chat_id).encode("ascii") not in chat_ids:
        r.lpush("chat_ids", chat_id)
        try:
            db["chats"].insert_one({"chat_id": chat_id, "chat_name": chat_name})
        except TypeError as e:
            context.bot_data["errorLogger"].error(
                f"Error while saving conversation id: {chat_id} name: {chat_name} info:\n{e}"
            )
