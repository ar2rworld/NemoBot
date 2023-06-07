import imp
import re
from random import random as rnd

from utils.listCaching import loadList, removeFromList

async def kolonka(update, context):
  await update.message.chat.send_message("Postaviat!" if rnd()>=0.5 else "Net, ne postaviat.")

async def osuzhdau(update, context):
    calling204Phrases = context.application.bot_data["calling204Phrases"]
    mat = context.application.bot_data["mat"]
    errorLogger = context.application.bot_data["errorLogger"]
    osuzhdatN=0
    try:
      mesdasage=update.message.text.lower()
      for m in mat:
          try:
            if(re.match(r".*"+str(m).lower()+".*", message)):
              osuzhdatN+=1
          except Exception as e:
            errorLogger.error(e)

      if(osuzhdatN!=0):
        await update.message.chat.send_message("осуждаю"+("."*osuzhdatN if osuzhdatN>0 else 1))
      if(re.match(r".*calling204.*", message)):
        if(len(calling204Phrases)==0):
          context.application.bot_data["calling204Phrases"] = { 'Haha, man, your are the best!' }
        n = int(rnd()*len(calling204Phrases))
        phrase = ""
        for i, key in enumerate( calling204Phrases ):
          if n == i:
            phrase = key
            break
        await update.message.chat.send_message(phrase)
    except Exception as e:
      print('Exception occured:', e)

async def osuzhdat(update, context):
    tokens=update.message.text.split(' ')
    r = context.application.bot_data["r"]

    if(len(tokens)==2 and tokens[1] != "-p" and tokens[1] != '-a'):
        n = loadList( r, context, "mat", tokens[1] )
        await update.message.chat.send_message("Got it! Let's make community better together!(words : " +str(n)+ ")")
    elif len(tokens) > 2 and tokens[1] == '-p':
        n = loadList (r, context, "mat", " ".join(tokens[2:]).lower() )
        await update.message.chat.send_message("Got your phrase, let's osuzhdat together!(" + str(n)+ ")")
    elif len(tokens)==2 and tokens[1]=='-a':
        await update.message.chat.send_message("I don't wanna see this words:\n" +\
            str( context.application.bot_data["mat"] ))
    else:
        await update.message.chat.send_message("Plz, i need the word u don't wanna hear/see")

async def neosuzhdat(update, context):
    r = context.application.bot_data["r"]
    mat = loadList(r, context, "mat")
    tokens = update.message.text.split(' ')

    if(len(tokens)==2 and tokens[1]!="-p"):
        n = removeFromList( r, context, "mat", tokens[1] )
        await update.message.chat.send_message("I hope that you making a wise decision, words deleted: " +str(n)+".")
    elif len(tokens)>2 and tokens[1]=='-p':
        n = removeFromList( r, context, "mat", " ".join(tokens[2:]) )
        await update.message.chat.send_message("I know you are a brave man, hope that you making a wise decision, phrases deleted: " +str(n)+".")
    else:
        await update.message.chat.send_message("I can't understan you, check my /help=(")
    context.application.bot_data["mat"] = loadList(r, context, "mat")

async def tvoichlen(update, context):
  await update.message.chat.send_message("Moi chlen!" if rnd()>=0.5 else "Tvoi chlen!")

async def test(update, context):
  await update.message.chat.send_message("test command")

async def addCalling204Help(update, context):
  tokens = update.message.text.split(" ")
  if(len(tokens)>1):
    r = context.application.bot_data["r"]
    phrase = " ".join(tokens[1:])
    result = loadList( r, context, "calling204Phrases", phrase )
    await update.message.chat.send_message("good: "+str(result))
    context.application.bot_data["calling204Phrases"].add( phrase )
    print("addCalling204Phrases len: " + str(result))
  else:
    await update.message.chat.send_message("Invalid args!")
