
from pymongo.database import Database
from redis import Redis
from telegram import Message
from telegram.ext import ContextTypes


def save_conversation(context: ContextTypes.DEFAULT_TYPE, message: Message) -> None:
    r: Redis = context.application.bot_data["r"]
    db: Database = context.application.bot_data["db"]
    # check if chat id is in redis
    chat_ids = r.lrange("chat_ids", 0, -1)
    chat_id = message["chat"]["id"]
    chat_title = message["chat"]["title"]
    username = message["chat"]["username"]
    chat_name = (chat_title or username).replace("'", "")

    if str(chat_id).encode("ascii") not in chat_ids:
        r.lpush("chat_ids", chat_id)
        try:
            db["chats"].insert_one({"chat_id": chat_id, "chat_name": chat_name})
        except TypeError as e:
            context.bot_data["errorLogger"].error(
                f"Error while saving conversation id: {chat_id} name: {chat_name} info:\n{e}"
            )
