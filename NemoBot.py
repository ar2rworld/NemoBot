import _thread
import datetime
import logging
import subprocess
from os import getenv

import redis
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram import Update
from telegram.ext import Application
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes
from telegram.ext import MessageHandler
from telegram.ext import filters

from src.handlers.echoHandler import echoHandler

# local functions
from src.handlers.room204 import addCalling204Help
from src.handlers.room204 import kolonka
from src.handlers.room204 import neosuzhdat
from src.handlers.room204 import osuzhdat
from src.handlers.room204 import tvoichlen
from src.handlers.send_message import send_message
from src.menus.menu import find_menu_in_context
from src.mongo.mongo_connection import accessMongo
from src.mongo.mongo_connection import check_mongo
from src.mongo.mongo_connection import get_client
from src.mongo.mongo_connection import load_collection
from src.mongo.mongo_connection import upsert_to_mongo
from src.my_menus.requestAccessMenu import setupRequestAccessMenu
from src.my_redis.inmemoryRedis import InmemoryRedis
from src.notificator.server import runServer
from src.notificator.subscribe import subscribe
from src.notificator.subscribe import subscribeToChannels
from src.socials_interactions.socials import post
from src.utils.alivePhrases import addAlivePhrases
from src.utils.echo import addEchoPhrase
from src.utils.echo_commands import my_telegram_id
from src.utils.listCaching import loadList
from src.utils.other import pickRandomFromList


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.chat.send_message("start command")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.chat.send_message(
        """
/postaviat
/tvoichlen
/osuzhdat <bad word>
/osuzhdat -p <bad phrase>
/osuzhdat -a
/neosuzhdat <bad word>
/neosuzhdat -p <bad phrase>
/my_telegram_id
/addCalling204Help <helping phrase>
add \"calling204\" when joking
/addAlivePhrases <phrase> [|,|<phrase>|,|<phrase>...]
Admin commands:
    /checkMongo <dbName> <tableName>
    /upsertToMongo <tableName> <json>
    /post
    /addEchoPhrase <phrase>|-|<answer>
    /subscribeToChannels
    /accessMongo [showTables] <insert|find|update|delete> <collectionName> [filter|<filter|-|json>]
    """
    )


async def test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.chat.send_message("yeah, this is a test command")


def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    error_logger = context.application.bot_data["errorLogger"]
    error_logger.error(update)
    error_logger.error(context.error)


def main():
    xml_parser_logger = logging.getLogger("xmlParser")
    xml_parser_logger.setLevel(logging.INFO)
    xml_parser_handler = logging.FileHandler("xmlBodyLocal.log", "a", "utf-8")
    xml_parser_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    xml_parser_logger.addHandler(xml_parser_handler)

    error_logger = logging.getLogger("errorLogger")
    error_logger.setLevel(logging.ERROR)
    error_logger_handler = logging.FileHandler("error.log", "a", "utf-8")
    error_logger_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    error_logger.addHandler(error_logger_handler)

    main_logger = logging.getLogger("mainLogger")
    main_logger.setLevel(logging.INFO)
    main_logger_handler = logging.FileHandler("main.log", "a", "utf-8")
    main_logger_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    main_logger.addHandler(main_logger_handler)

    main_logger.info("Starting...")

    server_logger = logging.getLogger("serverLogger")
    server_logger_handler = logging.FileHandler("server.log", "a", "utf-8")
    server_logger_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    server_logger.addHandler(server_logger_handler)

    app = Application.builder().token(getenv("NEMOBOTTOKEN")).build()

    db = get_client()[getenv("MONGO_DBNAME")]

    r = None
    if getenv("DEBUG"):
        r = InmemoryRedis(getenv("REDIS_HOST"), getenv("REDIS_PORT"))
    else:
        r = redis.Redis(getenv("REDIS_HOST"), int(getenv("REDIS_PORT")))
        try:
            if r.ping():
                main_logger.info("Redis is ready")
        except Exception as e:
            error_logger.error(e)
            main_logger.error("Redis is not ready")
            raise e

    app.bot_data["r"] = r
    app.bot_data["db"] = db
    app.bot_data["mainLogger"] = main_logger
    app.bot_data["errorLogger"] = error_logger
    app.bot_data["findMenuInContext"] = find_menu_in_context
    app.bot_data["callbackUrl"] = getenv("CALLBACKURL")
    app.bot_data["hubUrl"] = getenv("HUBURL")
    app.bot_data["tg_my_id"] = getenv("TG_MY_ID")
    app.bot_data["adminId"] = getenv("TG_MY_ID")
    app.bot_data["calling204Phrases"] = set(loadList(r, context=None, listName="calling204Phrases"))
    app.bot_data["echoPhrases"] = load_collection(db, "echoPhrases")
    app.bot_data["alivePhrases"] = load_collection(db, "alivePhrases") or [{"phrase": "I am alive"}]
    app.bot_data["mat"] = set(loadList(r, context=None, listName="mat"))
    app.bot_data["botChannel"] = getenv("BOTCHANNEL")
    app.bot_data["botGroup"] = getenv("BOTGROUP")
    app.bot_data["callbackQueryHandlers"] = {}
    app.bot_data["echoHandlers"] = {}

    setupRequestAccessMenu(app, db)
    # setupRequestsViewMenu(app, db)

    app.bot_data["findMenuInContext"] = find_menu_in_context

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("postaviat", kolonka))
    app.add_handler(CommandHandler("tvoichlen", tvoichlen))
    app.add_handler(CommandHandler("osuzhdat", osuzhdat))
    app.add_handler(CommandHandler("neosuzhdat", neosuzhdat))
    app.add_handler(CommandHandler("my_telegram_id", my_telegram_id))
    app.add_handler(CommandHandler("addCalling204Help", addCalling204Help))
    app.add_handler(CommandHandler("test", test))
    app.add_handler(CommandHandler("post", post))
    app.add_handler(CommandHandler("send_message", send_message))
    app.add_handler(CommandHandler("accessMongo", accessMongo))
    app.add_handler(CommandHandler("checkMongo", check_mongo))
    app.add_handler(CommandHandler("upsertToMongo", upsert_to_mongo))
    app.add_handler(CommandHandler("subscribeToChannels", subscribeToChannels))
    app.add_handler(CommandHandler("addEchoPhrase", addEchoPhrase))
    app.add_handler(CommandHandler("addAlivePhrases", addAlivePhrases))
    app.add_handler(MessageHandler(filters.TEXT, echoHandler))

    def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        func = context.application.bot_data["callbackQueryHandlers"][update.callback_query.data]
        if not func:
            raise Exception(f'Callback query handler: "{update.callback_query.data}" not found')
        func(update, context)

    app.add_handler(CallbackQueryHandler(callback_query_handler))
    app.add_error_handler(error)

    _thread.start_new_thread(runServer, (app, db, getenv("NOTIFICATOR_HOST"), getenv("NOTIFICATOR_PORT")))
    app.job_queue.run_daily(lambda x: subscribe(app), datetime.time(0, 0))

    async def send_alive_message(context: ContextTypes.DEFAULT_TYPE):
        # send alive messages
        await app.bot.send_message(
            app.bot_data["tg_my_id"],
            "hello comrade!",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("/help")], [KeyboardButton("/requestAccess")]]),
        )
        if not getenv("DEBUG"):
            commits = subprocess.check_output(["git", "log"]).decode("utf-8")
            last_commit = commits[commits.find("Author", 1): commits.find("commit", 1)].replace("\n", "")
            phrase = pickRandomFromList(app.bot_data["alivePhrases"])["phrase"]
            channel_post = f"{last_commit}\n{phrase}"
            await app.bot.send_message(app.bot_data["botChannel"], channel_post)
            await app.bot.send_message(app.bot_data["botGroup"], phrase)

    app.job_queue.run_once(send_alive_message, 0)

    main_logger.info("Started")
    app.run_polling()


if __name__ == "__main__":
    main()
