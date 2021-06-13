import os
from telegram.ext import *
from telegram import KeyboardButton
from random import random as rnd
import re
import redis
mat=[]
r=redis.Redis("localhost", 6379)
print("Starting...")

def loadMats(word=""):
    if(word==""):
        mats = r.lrange("mat", 0, -1)
        words=[w.decode("utf-8") for w in mats]
        return words
    else:
        return r.lpush("mat", word)

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
            ")

def error(update, context):
    print(update)
    print(context.error)
    pass

def kolonka(update, context):
    update.message.chat.send_message("Postaviat!" if rnd()>=0.5 else "Net, ne postaviat.")

def osuzhdau(update, context):
  osuzhdatN=0
  message=update.message.text.lower()
  #print(mat)
  for m in mat:
    #print(re.match(r".*"+m.lower()+".*", message) + "-|")
    if(re.match(r".*"+m.lower()+".*", message)):
      #print("osuzhdenie")    
      osuzhdatN+=1
  #match=re.match(r".*"+"ХУЙ".lower()+".*", message)
  #print(match)
  if(osuzhdatN!=0):
    update.message.chat.send_message("осуждаю"+("."*osuzhdatN if osuzhdatN>0 else 1))
  if(re.match(r".*calling204.*", message)):
    update.message.chat.send_message("Haha(i'm here for u)")
    print("found help")
    
'''def callingTOF(update, context):
  if(re.match(r".*calling204.*", message)):
    update.message.chat.send_message("Haha(i'm here for u)")
    print("found help")
  message=update.message.text.lower()
  else:
    print("not here")'''
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

def main():
    global mat
    updater=Updater(os.environ["NemoBotToken"], use_context=True)
    mat=loadMats()
    dp=updater.dispatcher
    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("postaviat", kolonka))
    dp.add_handler(CommandHandler("tvoichlen", tvoichlen))
    dp.add_handler(CommandHandler("osuzhdat", osuzhdat))
    dp.add_handler(CommandHandler("neosuzhdat", neosuzhdat))
    dp.add_handler(CommandHandler("test", test))
    dp.add_handler(MessageHandler(Filters.chat_type , osuzhdau))
    #dp.add_handler(MessageHandler(Filters.chat_type , callingTOF))
    dp.add_error_handler(error)
    updater.start_polling(1)
    updater.idle()

main()

