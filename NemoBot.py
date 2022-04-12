import subprocess
from os import getenv
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
from telegram.ext.filters import Filters
import redis
import _thread
import logging
from decorators.adminOnly import adminOnly
from menus.menu import Menu, findMenuInContext

#local functions
from room204 import addCalling204Help, loadList, kolonka, tvoichlen, osuzhdat, neosuzhdat
from echoHandler import echoHandler
from socials import post
from send_message import send_message
from utils.echo_commands import my_telegram_id
from utils.echo import addEchoPhrase
from utils.alivePhrases import addAlivePhrases
from utils.other import pickRandomFromList
from mongo_connection import get_client, check_mongo, addToCollection, loadCollection, upsertToMongo
from notificator.server import runServer
from notificator.subscribe import subscribe, subscribeToChannels

print("Starting...")

def start_command(update, context):
    update.message.chat.send_message("start command")

def help_command(update, context):
    update.message.chat.send_message('''
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
    /check_mongo <dbName> <tableName>
    /upsertToMongo <tableName> <json>
    /post
    /addEchoPhrase <phrase>|-|<answer>
    /subscribeToChannels
    ''')

def test(update, context):
    update.message.chat.send_message("yeah, this is a test command")

def error(update, context):
    if getenv("DEBUG") == "True":
        print('Update "%s"\n\nCaused error "%s"' % (update, context.error))
    errorLogger = context.dispatcher.user_data["errorLogger"]
    errorLogger.error(update)
    errorLogger.error(context.error)
    
def main():
    xmlParserLogger = logging.getLogger("xmlParser")
    xmlParserLogger.setLevel(logging.INFO)
    xmlParserHandler = logging.FileHandler("xmlBodyLocal.log", "a", "utf-8")
    xmlParserHandler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    xmlParserLogger.addHandler(xmlParserHandler)

    errorLogger = logging.getLogger("errorLogger")
    errorLogger.setLevel(logging.ERROR)
    errorLoggerHandler = logging.FileHandler("error.log", "a", "utf-8")
    errorLoggerHandler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    errorLogger.addHandler(errorLoggerHandler)

    mainLogger = logging.getLogger("mainLogger")
    mainLogger.setLevel(logging.INFO)
    mainLoggerHandler = logging.FileHandler("main.log", "a", "utf-8")
    mainLoggerHandler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    mainLogger.addHandler(mainLoggerHandler)

    updater=Updater(getenv("NemoBotToken"), use_context=True)
    
    db = get_client()[getenv("mongo_dbname")]

    r=redis.Redis(getenv('redis_host'), getenv('redis_port'))
    try:
        if r.ping():
            mainLogger.info("Redis is ready")
    except Exception as e:
        errorLogger.error(e)
        mainLogger.error("Redis is not ready")
        raise e
    
    dp=updater.dispatcher
    dp.user_data["r"]   = r
    dp.user_data["db"]  = db
    dp.user_data["mainLogger"]            = mainLogger
    dp.user_data["errorLogger"]           = errorLogger
    dp.user_data["findMenuInContext"]     = findMenuInContext
    dp.user_data["callbackUrl"]           = getenv("callbackUrl")
    dp.user_data["hubUrl"]                = getenv("hubUrl")
    dp.user_data["tg_my_id"]              = getenv("tg_my_id")
    dp.user_data["adminId"]               = getenv("tg_my_id")
    dp.user_data["calling204Phrases"]     = set(loadList(r, context=None, listName="calling204Phrases"))
    dp.user_data["echoPhrases"]           = loadCollection(db, "echoPhrases")
    dp.user_data["alivePhrases"]          = loadCollection(db, "alivePhrases") or [{"phrase" : "I am alive"}]
    dp.user_data["mat"]                   = set(loadList(r, context=None, listName="mat"))
    dp.user_data["botChannel"]            = getenv("botChannel")
    dp.user_data["botGroup"]              = getenv("botGroup")
    dp.user_data["callbackQueryHandlers"] = {}
    dp.user_data["echoHandlers"]       = []

    def userInputEchoHandler(update : Update, context : CallbackContext):
            user_data = context.dispatcher.user_data
            userInput = update.message.text
            context.dispatcher.user_data["echoHandlers"].remove(userInputEchoHandler)
            db = user_data["db"]
            userId = update.message.from_user.id
            menuObj = db.userInput.find_one({ "userId" : userId })
            if not menuObj:
                return
            menu = user_data[menuObj["menuName"]]
            db.userInput.update_one({ "userId" : userId }, { "$set" : { "userInput" : userInput, "status" : 1 } }, upsert=True)
            menu.renderScreen(userId, "thankYouScreen")
            
    menu = Menu("requestAccess", command="requestAccess", dispatcher=dp, db=db, echoHandlers=[userInputEchoHandler])
    def authorizeAddEchoPhrase(update, context):
        user_data = context.dispatcher.user_data
        menu = user_data["findMenuInContext"](update, context)
        menu.renderScreen(update.callback_query.from_user.id, "reasonScreen")
    def upsertToMongoCallbackQuery(update, context):
        user_data = context.dispatcher.user_data
        menu = user_data["findMenuInContext"](update, context)
        menu.renderScreen(update.callback_query.from_user.id, "reasonScreen")
    def checkMongoCallbackQuery(update, context):
        user_data = context.dispatcher.user_data
        menu = user_data["findMenuInContext"](update, context)
        context.dispatcher.user_data["echoHandlers"].append(userInputEchoHandler)
        menuName = menu.renderScreen(update.callback_query.from_user.id, "reasonScreen")
        db = user_data["db"]
        db.userInput.update_one({ "userId" : update.callback_query.from_user.id },
            { "$set" : { "menuName" : menuName, "status" : 0 }},
            upsert=True)
    menu.addScreenObj({"text" : "Choose command to request access:",
                    "name" : "firstScreen",
                    "rows" : [
                        [
                            {"text" : "addEchoPhrase", "callbackData" : "addEchoPhraseCallbackQuery",
                            "callbackFunction" : authorizeAddEchoPhrase},
                            {"text" : "check_mongo", "callbackData" : "checkMongoCallbackQuery",
                            "callbackFunction" : checkMongoCallbackQuery}
                        ],
                        [
                            {"text" : "upsertToMongo", "callbackData" : "upsertToMongo",
                            "callbackFunction" : upsertToMongoCallbackQuery}
                        ]
                    ]})
    menu.addScreenObj({"text" : "Second screen",
                    "name" : "secondScreen",
                    "rows" : [
                        [{"text" : "one button", "callbackData" : "addEchoPhraseCallbackQuery",
                        "callbackFunction" : authorizeAddEchoPhrase}],
                    ]})
    menu.addScreenObj({"text" : "Thank you for your request",
                    "name" : "thankYouScreen"})
    menu.addScreenObj({"text" : "Invalid input(empty)",
                    "name" : "emptyInputScreen"})
    menu.addScreenObj({"text" : "Why would you need this command?",
                    "name" : "reasonScreen",
                    "callback" : "reasonScren"})
                    #                    
    # TODO: add entering text functionality to the menu ^
    menu.build()

    dp.user_data[menu.name] = menu
    dp.user_data["findMenuInContext"] = findMenuInContext

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
    dp.add_handler(CommandHandler("upsertToMongo", upsertToMongo))
    dp.add_handler(CommandHandler("subscribeToChannels" , subscribeToChannels))
    dp.add_handler(CommandHandler("addEchoPhrase", addEchoPhrase))
    dp.add_handler(CommandHandler("addAlivePhrases", addAlivePhrases))
    #dp.add_handler(CommandHandler("requestAccess", requestAccess))
    dp.add_handler(MessageHandler(Filters.update.message , echoHandler, run_async=True))
    
    def callbackQueryHandler(update, context):
        func = context.dispatcher.user_data["callbackQueryHandlers"][update.callback_query.data]
        if not func:
            raise Exception(f"Callback query handler: \"{update.callback_query.data}\" not found")
        func(update, context)

    dp.add_handler(CallbackQueryHandler(callbackQueryHandler))
    dp.add_error_handler(error)

    _thread.start_new_thread(runServer, (dp, db, getenv('notificator_host'), getenv('notificator_port')))
    dp.job_queue.run_repeating(lambda x: subscribe(dp), 86400, first=1)

    # send alive messages
    dp.bot.send_message(dp.user_data["tg_my_id"], "hello comrade!",reply_markup=ReplyKeyboardMarkup([
        [KeyboardButton("/help")],
        [KeyboardButton("/requestAccess")]
    ]))
    if not getenv("DEBUG"):
        commits = subprocess.check_output(["git", "log"]).decode("utf-8")
        lastCommit = commits[commits.find('Author',1) : commits.find('commit', 1)].replace("\n", "")
        phrase = pickRandomFromList(dp.user_data["alivePhrases"])["phrase"]
        channelPost = f'{lastCommit}\n{phrase}'
        dp.bot.send_message(dp.user_data["botChannel"], channelPost)
        dp.bot.send_message(dp.user_data["botGroup"], phrase)

    updater.start_polling(1)
    updater.idle()

main()
