from os import getenv
from telegram.ext import *
from telegram import KeyboardButton
import redis
import _thread
import logging
from decorators.adminOnly import adminOnly

#local functions
from room204 import addCalling204Help, loadList, kolonka, osuzhdau, tvoichlen, osuzhdat, neosuzhdat 
from socials import post
from send_message import send_message
from echo_commands import my_telegram_id
from mongo_connection import get_client, check_mongo
from notificator.server import runServer
from notificator.subscribe import subscribe, subscribeToChannels

logging.basicConfig(filename='error.log', encoding='utf-8', level=logging.DEBUG)

print("Starting...")

def start_command(update, context):
    update.message.chat.send_message("start command")

def help_command(update, context):
    update.message.chat.send_message("/postaviat\n/tvoichlen\n\
            /osuzhdat <bad word>\n\
            /osuzhdat -p <bad phrase>\n\
            /osuzhdat -a\n\
            /neosuzhdat <bad word>\n\
            /neosuzhdat -p <bad phrase>\n\
            /my_telegram_id\n\
            /addCalling204Help <helping phrase>\n\
            add \"calling204\" when joking\n\
            /check_mongo <dbName> <tableName>\
            ")

def test(update, context):
    update.message.chat.send_message("yeah, this is a test command")

def error(update, context):
    logging.error(update)
    logging.error(context.error)
    
def main():
    updater=Updater(getenv("NemoBotToken"), use_context=True)
    
    db = get_client()[getenv("mongo_dbname")]
    r=redis.Redis(getenv('redis_host'), getenv('redis_port'))

    calling204Phrases=[]
    
    dp=updater.dispatcher

    dp.user_data["db"] = db
    dp.user_data["callbackUrl"] = getenv("callbackUrl")
    dp.user_data["hubUrl"] = getenv("hubUrl")
    dp.user_data["tg_my_id"] = getenv("tg_my_id")
    dp.user_data["calling204Phrases"] = set( loadList( r, context=None, listName="calling204Phrases" ) )
    dp.user_data["r"] = r
    dp.user_data["mat"] = set(loadList(r, context=None, listName="mat"))

    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("postaviat", kolonka))
    dp.add_handler(CommandHandler("tvoichlen", tvoichlen))
    dp.add_handler(CommandHandler("osuzhdat", osuzhdat))
    dp.add_handler(CommandHandler("neosuzhdat", neosuzhdat))
    dp.add_handler(CommandHandler("my_telegram_id", my_telegram_id))
    dp.add_handler(CommandHandler("addCalling204Help", addCalling204Help))
    dp.add_handler(CommandHandler("test", test))
    dp.add_handler(CommandHandler("post", post))
    dp.add_handler(CommandHandler("send_message", send_message))
    dp.add_handler(CommandHandler("check_mongo", check_mongo))
    dp.add_handler(CommandHandler("subscribeToChannels" , subscribeToChannels))
    dp.add_handler(MessageHandler(Filters.chat_type , osuzhdau))
    dp.add_error_handler(error)

    _thread.start_new_thread(runServer, (dp, db, getenv('notificator_host'), getenv('notificator_port')))
    dp.job_queue.run_repeating(lambda x: subscribe(dp), 86400, first=1)

    dp.bot.send_message(dp.user_data["tg_my_id"], "hello comrade!")  
    updater.start_polling(1)
    updater.idle()

main()
