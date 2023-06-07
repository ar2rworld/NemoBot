import datetime
import subprocess
from os import getenv
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, Bot
from telegram.ext import (
  Application,
  CommandHandler,
  MessageHandler,
  CallbackQueryHandler,
  CallbackContext,
  filters,
  ContextTypes
)
import redis
import _thread
import logging
from decorators.adminOnly import adminOnly
from menus.menu import findMenuInContext
from myRedis.inmemoryRedis import InmemoryRedis
from requestsViewMenu import setupRequestsViewMenu

#local functions
from room204 import addCalling204Help, loadList, kolonka, tvoichlen, osuzhdat, neosuzhdat
from echoHandler import echoHandler
from socials import post
from send_message import send_message
from utils.echo_commands import my_telegram_id
from utils.echo import addEchoPhrase
from utils.alivePhrases import addAlivePhrases
from utils.other import pickRandomFromList
from mongo_connection import accessMongo, get_client, checkMongo, addToCollection, loadCollection, upsertToMongo
from notificator.server import runServer
from notificator.subscribe import subscribe, subscribeToChannels
from requestAccessMenu import setupRequestAccessMenu

async def start_command(update, context):
    await update.message.chat.send_message("start command")

async def help_command(update, context):
    await update.message.chat.send_message('''
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
    ''')

async def test(update, context):
  await update.message.chat.send_message("yeah, this is a test command")

def error(update, context):
  if getenv("DEBUG") == "True":
      print('Update "%s"\n\nCaused error "%s"' % (update, context.error))
  errorLogger = context.application.bot_data["errorLogger"]
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

  mainLogger.info("Starting...")

  serverLogger = logging.getLogger("serverLogger")
  serverLoggerHandler = logging.FileHandler("server.log", "a", "utf-8")
  serverLoggerHandler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
  serverLogger.addHandler(serverLoggerHandler)

  app = Application.builder().token(getenv("NemoBotToken")).build()
  
  db = get_client()[getenv("mongo_dbname")]

  r = None
  if getenv("DEBUG"):
      r = InmemoryRedis(getenv("redis_host"), getenv("redis_port"))
  else:
      r = redis.Redis(getenv('redis_host'), getenv('redis_port'))
      try:
          if r.ping():
              mainLogger.info("Redis is ready")
      except Exception as e:
          errorLogger.error(e)
          mainLogger.error("Redis is not ready")
          raise e

  app.bot_data["r"]   = r
  app.bot_data["db"]  = db
  app.bot_data["mainLogger"]            = mainLogger
  app.bot_data["errorLogger"]           = errorLogger
  app.bot_data["findMenuInContext"]     = findMenuInContext
  app.bot_data["callbackUrl"]           = getenv("callbackUrl")
  app.bot_data["hubUrl"]                = getenv("hubUrl")
  app.bot_data["tg_my_id"]              = getenv("tg_my_id")
  app.bot_data["adminId"]               = getenv("tg_my_id")
  app.bot_data["calling204Phrases"]     = set(loadList(r, context=None, listName="calling204Phrases"))
  app.bot_data["echoPhrases"]           = loadCollection(db, "echoPhrases")
  app.bot_data["alivePhrases"]          = loadCollection(db, "alivePhrases") or [{"phrase" : "I am alive"}]
  app.bot_data["mat"]                   = set(loadList(r, context=None, listName="mat"))
  app.bot_data["botChannel"]            = getenv("botChannel")
  app.bot_data["botGroup"]              = getenv("botGroup")
  app.bot_data["callbackQueryHandlers"] = {}
  app.bot_data["echoHandlers"]          = {}

  menu = setupRequestAccessMenu(app, db)
  #setupRequestsViewMenu(app, db)

  app.bot_data["findMenuInContext"] = findMenuInContext

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
  app.add_handler(CommandHandler("checkMongo", checkMongo))
  app.add_handler(CommandHandler("upsertToMongo", upsertToMongo))
  app.add_handler(CommandHandler("subscribeToChannels" , subscribeToChannels))
  app.add_handler(CommandHandler("addEchoPhrase", addEchoPhrase))
  app.add_handler(CommandHandler("addAlivePhrases", addAlivePhrases))
  app.add_handler(MessageHandler(filters.TEXT, echoHandler))
  
  def callbackQueryHandler(update, context):
      func = context.application.bot_data["callbackQueryHandlers"][update.callback_query.data]
      if not func:
          raise Exception(f"Callback query handler: \"{update.callback_query.data}\" not found")
      func(update, context)

  app.add_handler(CallbackQueryHandler(callbackQueryHandler))
  app.add_error_handler(error)

  _thread.start_new_thread(runServer, (app, db, getenv('notificator_host'), getenv('notificator_port')))
  app.job_queue.run_daily(lambda x: subscribe(app), datetime.time(0, 0))

  async def sendAliveMessage(context: ContextTypes.DEFAULT_TYPE):
    # send alive messages
    await app.bot.send_message(app.bot_data["tg_my_id"], "hello comrade!",reply_markup=ReplyKeyboardMarkup([
      [KeyboardButton("/help")],
      [KeyboardButton("/requestAccess")]
    ]))
    if not getenv("DEBUG"):
      commits = subprocess.check_output(["git", "log"]).decode("utf-8")
      lastCommit = commits[commits.find('Author',1) : commits.find('commit', 1)].replace("\n", "")
      phrase = pickRandomFromList(app.bot_data["alivePhrases"])["phrase"]
      channelPost = f'{lastCommit}\n{phrase}'
      await app.bot.send_message(app.bot_data["botChannel"], channelPost)
      await app.bot.send_message(app.bot_data["botGroup"], phrase)
  
  app.job_queue.run_once(sendAliveMessage, 0)

  mainLogger.info("Started")
  app.run_polling()

main()

# TODO write some tests for handlers
