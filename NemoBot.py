from os import getenv
from telegram.ext import *
from telegram import KeyboardButton
from random import random as rnd
import re
import redis
import _thread
import logging

#local functions
from socials import post
from stats import save_conversation
from send_message import send_message
from echo_commands import my_telegram_id
from mongo_connection import get_client, check_mongo
from notificator.server import runServer
from notificator.subscribe import subscribe

mat=[]
calling204Phrases=[]
r=redis.Redis(getenv('redis_host'), getenv('redis_port'))

logging.basicConfig(filename='error.log', encoding='utf-8', level=logging.DEBUG)

print("Starting...")

def loadMats(word=""):
    if(word==""):
        mats = r.lrange("mat", 0, -1)
        words=[w.decode("utf-8") for w in mats]
        return words
    else:
        return r.lpush("mat", word)

def addCalling204(word=""): 
    if(word==""):
        mats=r.lrange("calling204", 0, -1)
        words=[w.decode("utf-8") for w in mats]
        return words
    else:
        return r.lpush("calling204", word)

def removeFromList(list, key, n=100):
    return r.lrem(list, n, key)

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

def error(update, context):
    logging.error(update)
    logging.error(context.error)
    
def kolonka(update, context):
    update.message.chat.send_message("Postaviat!" if rnd()>=0.5 else "Net, ne postaviat.")

def osuzhdau(update, context):
  global calling204Phrases
  osuzhdatN=0
  try:
    message=update.message.text.lower()
    
    save_conversation(r, update.message)

    for m in mat:
        if(re.match(r".*"+m.lower()+".*", message)):
            osuzhdatN+=1
    #print(match)
    if(osuzhdatN!=0):
        update.message.chat.send_message("осуждаю"+("."*osuzhdatN if osuzhdatN>0 else 1))
    if(re.match(r".*calling204.*", message)):
        if(len(calling204Phrases)==0):
            calling204Phrases=addCalling204()
            if(len(calling204Phrases)==0):
                calling204Phrases=['Haha, man, your are the best!']
        update.message.chat.send_message(calling204Phrases[int(rnd()*len(calling204Phrases))])#"Haha(i'm here for u)")
        print("found help")
  except Exception as e:
    print('Exception occured:', e)

def osuzhdat(update, context):
    global mat
    #print(loadMats())
    tokens=update.message.text.split(' ')
    if(len(tokens)==2 and tokens[1]!="-p" and tokens[1]!='-a'):
        n=loadMats(tokens[1])
        update.message.chat.send_message("Got it! Let's make community better together!(words : " +str(n)+ ")")
    elif len(tokens)>2 and tokens[1]=='-p':
        n=loadMats(" ".join(tokens[2:]).lower())
        update.message.chat.send_message("Got your phrase, let's osuzhdat together!(" + str(n)+ ")")
    elif len(tokens)==2 and tokens[1]=='-a':
        update.message.chat.send_message("Osuzhdau those words:\n" + str(loadMats()))
    else:
        update.message.chat.send_message("Plz, i need the word u don't wanna hear/see")
    mat=loadMats()


def neosuzhdat(update, context):
    global mat
    tokens=update.message.text.split(' ')
    if(len(tokens)==2 and tokens[1]!="-p"):
        n=removeFromList("mat", tokens[1])
        update.message.chat.send_message("I hope that you making a wise decision, words deleted: " +str(n)+".")
    elif len(tokens)>2 and tokens[1]=='-p':
        n=removeFromList("mat", " ".join(tokens[2:]))
        update.message.chat.send_message("I know you are a brave man, hope that you making a wise decision, phrases deleted: " +str(n)+".")
    else:
        update.message.chat.send_message("I can't understan you, check my /help=(")
    mat = loadMats()

def tvoichlen(update, context):
  update.message.chat.send_message("Moi chlen!" if rnd()>=0.5 else "Tvoi chlen!")

def test(update, context):
    update.message.chat.send_message("test command")

def addCalling204Help(update, context):
    global calling204Phrases
    phrase=update.message.text.split(" ")
    if(len(phrase)>1):
        result=addCalling204(" ".join(phrase[1:]))
        update.message.chat.send_message("good: "+str(result))
        calling204Phrases=addCalling204()
        print("addCalling204Phrases len: " + str(result))
    else:
        update.message.chat.send_message("Invalid args!")

def main():
    global mat
    updater=Updater(getenv("NemoBotToken"), use_context=True)
    mat=loadMats()
    db = get_client()[getenv("mongo_dbname")]
    dp=updater.dispatcher
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
    dp.add_handler(MessageHandler(Filters.chat_type , osuzhdau))
    #dp.add_handler(MessageHandler(Filters.chat_type , callingTOF))
    dp.add_error_handler(error)

    _thread.start_new_thread(runServer, (dp, db, getenv('notification_host'), getenv('notificator_port')))
    dp.job_queue.run_repeating(lambda x: subscribe(dp, db, getenv("callbackUrl"), getenv("hubUrl"), getenv("tg_my_id") ), 86400, first=1)

    dp.bot.send_message(getenv("tg_my_id"), "hello comrade!")  
    updater.start_polling(1)
    updater.idle()

main()
