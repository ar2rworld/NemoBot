import _thread
import datetime
import logging
from logging import Logger
from os import getenv

from telegram.ext import Application
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import filters

from src.handlers.basic import error
from src.handlers.basic import help_command
from src.handlers.basic import start_command
from src.handlers.basic import test
from src.handlers.callback_query_handler import callback_query_handler
from src.handlers.context_executors import send_alive_message
from src.handlers.echo_handler import echo_handler

# local functions
from src.handlers.room204 import add_calling_204_help
from src.handlers.room204 import kolonka
from src.handlers.room204 import neosuzhdat
from src.handlers.room204 import osuzhdat
from src.handlers.room204 import tvoichlen
from src.handlers.send_message import send_message
from src.menus.menu import find_menu_in_context
from src.mongo.mongo_connection import access_mongo
from src.mongo.mongo_connection import check_mongo
from src.mongo.mongo_connection import get_client
from src.mongo.mongo_connection import load_collection
from src.mongo.mongo_connection import upsert_to_mongo
from src.my_menus.request_access_menu import setup_request_access_menu
from src.my_redis.setup_redis import setup_redis
from src.notificator.run_server import run_server
from src.notificator.subscribe import subscribe
from src.notificator.subscribe import subscribe_to_channels
from src.socials_interactions.socials import post
from src.utils.alive_phrases import add_alive_phrases
from src.utils.echo import add_echo_phrase
from src.utils.echo_commands import my_telegram_id
from src.utils.list_caching import load_list
from src.utils.other import get_environment_vars


def main() -> None:
    xml_parser_logger, error_logger, main_logger, server_logger = setup_loggers()

    main_logger.info("Starting...")

    nemobottoken = get_environment_vars("NEMOBOTTOKEN")[0]
    app = Application.builder().token(nemobottoken).build()

    db = get_client()[get_environment_vars("MONGO_DBNAME")[0]]

    redis_host, redis_port = get_environment_vars("REDIS_HOST", "REDIS_PORT")

    r = setup_redis(getenv("DEBUG"), error_logger, main_logger, redis_host, redis_port)

    app.bot_data["r"] = r
    app.bot_data["db"] = db
    app.bot_data["mainLogger"] = main_logger
    app.bot_data["errorLogger"] = error_logger
    app.bot_data["findMenuInContext"] = find_menu_in_context
    app.bot_data["callbackUrl"], app.bot_data["hubUrl"] = get_environment_vars("CALLBACKURL", "HUBURL")
    app.bot_data["tg_my_id"], app.bot_data["adminId"] = get_environment_vars("TG_MY_ID", "TG_MY_ID")
    app.bot_data["calling204Phrases"] = set(load_list(r, "calling204Phrases"))
    app.bot_data["echoPhrases"] = load_collection(db, "echoPhrases")
    app.bot_data["alivePhrases"] = load_collection(db, "alivePhrases") or [{"phrase": "I am alive"}]
    app.bot_data["mat"] = set(load_list(r, "mat"))
    app.bot_data["botChannel"], app.bot_data["botGroup"] = get_environment_vars("BOTCHANNEL", "BOTGROUP")
    app.bot_data["callbackQueryHandlers"] = {}
    app.bot_data["echoHandlers"] = {}

    setup_request_access_menu(app, db)

    app.bot_data["findMenuInContext"] = find_menu_in_context

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("postaviat", kolonka))
    app.add_handler(CommandHandler("tvoichlen", tvoichlen))
    app.add_handler(CommandHandler("osuzhdat", osuzhdat))
    app.add_handler(CommandHandler("neosuzhdat", neosuzhdat))
    app.add_handler(CommandHandler("my_telegram_id", my_telegram_id))
    app.add_handler(CommandHandler("addCalling204Help", add_calling_204_help))
    app.add_handler(CommandHandler("test", test))
    app.add_handler(CommandHandler("post", post))
    app.add_handler(CommandHandler("send_message", send_message))
    app.add_handler(CommandHandler("accessMongo", access_mongo))
    app.add_handler(CommandHandler("checkMongo", check_mongo))
    app.add_handler(CommandHandler("upsertToMongo", upsert_to_mongo))
    app.add_handler(CommandHandler("subscribeToChannels", subscribe_to_channels))
    app.add_handler(CommandHandler("addEchoPhrase", add_echo_phrase))
    app.add_handler(CommandHandler("addAlivePhrases", add_alive_phrases))
    app.add_handler(MessageHandler(filters.TEXT, echo_handler))

    app.add_handler(CallbackQueryHandler(callback_query_handler))
    app.add_error_handler(error)

    notificator_host, notificator_port = get_environment_vars("NOTIFICATOR_HOST", "NOTIFICATOR_PORT")
    _thread.start_new_thread(run_server, (app, db, notificator_host, notificator_port))

    setup_app_job_queue(app)

    main_logger.info("Started")
    app.run_polling()


def setup_app_job_queue(app: Application) -> None:
    if app.job_queue is None:
        msg = "Missing job_queue in application"
        raise ValueError(msg)
    app.job_queue.run_daily(subscribe, datetime.time(0, 0))

    app.job_queue.run_once(send_alive_message, 0)


def setup_loggers() -> tuple[Logger, Logger, Logger, Logger]:
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

    server_logger = logging.getLogger("serverLogger")
    server_logger_handler = logging.FileHandler("server.log", "a", "utf-8")
    server_logger_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    server_logger.addHandler(server_logger_handler)
    return xml_parser_logger, error_logger, main_logger, server_logger


if __name__ == "__main__":
    main()
