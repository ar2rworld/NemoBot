import imp
import re
from random import random as rnd

from utils.listCaching import loadList, removeFromList

def kolonka(update, context):
    update.message.chat.send_message("Postaviat!" if rnd()>=0.5 else "Net, ne postaviat.")

def osuzhdau(update, context):
    calling204Phrases = context.dispatcher.user_data["calling204Phrases"]
    mat = context.dispatcher.user_data["mat"]
    errorLogger = context.dispatcher.user_data["errorLogger"]
    osuzhdatN=0
    try:
        message=update.message.text.lower()
        for m in mat:
            try:
                if(re.match(r".*"+str(m).lower()+".*", message)):
                    osuzhdatN+=1
            except Exception as e:
                errorLogger.error(e)

        if(osuzhdatN!=0):
            update.message.chat.send_message("осуждаю"+("."*osuzhdatN if osuzhdatN>0 else 1))
        if(re.match(r".*calling204.*", message)):
            if(len(calling204Phrases)==0):
                context.dispatcher.user_data["calling204Phrases"] = { 'Haha, man, your are the best!' }
            n = int(rnd()*len(calling204Phrases))
            phrase = ""
            for i, key in enumerate( calling204Phrases ):
                if n == i:
                    phrase = key
                    break
            update.message.chat.send_message(phrase)
    except Exception as e:
        print('Exception occured:', e)

def osuzhdat(update, context):
    tokens=update.message.text.split(' ')
    r = context.dispatcher.user_data["r"]

    if(len(tokens)==2 and tokens[1] != "-p" and tokens[1] != '-a'):
        n = loadList( r, context, "mat", tokens[1] )
        update.message.chat.send_message("Got it! Let's make community better together!(words : " +str(n)+ ")")
    elif len(tokens) > 2 and tokens[1] == '-p':
        n = loadList (r, context, "mat", " ".join(tokens[2:]).lower() )
        update.message.chat.send_message("Got your phrase, let's osuzhdat together!(" + str(n)+ ")")
    elif len(tokens)==2 and tokens[1]=='-a':
        update.message.chat.send_message("I don't wanna see this words:\n" +\
            str( context.dispatcher.user_data["mat"] ))
    else:
        update.message.chat.send_message("Plz, i need the word u don't wanna hear/see")

def neosuzhdat(update, context):
    r = context.dispatcher.user_data["r"]
    mat = loadList(r, context, "mat")
    tokens = update.message.text.split(' ')

    if(len(tokens)==2 and tokens[1]!="-p"):
        n = removeFromList( r, context, "mat", tokens[1] )
        update.message.chat.send_message("I hope that you making a wise decision, words deleted: " +str(n)+".")
    elif len(tokens)>2 and tokens[1]=='-p':
        n = removeFromList( r, context, "mat", " ".join(tokens[2:]) )
        update.message.chat.send_message("I know you are a brave man, hope that you making a wise decision, phrases deleted: " +str(n)+".")
    else:
        update.message.chat.send_message("I can't understan you, check my /help=(")
    context.dispatcher.user_data["mat"] = loadList(r, context, "mat")

def tvoichlen(update, context):
    update.message.chat.send_message("Moi chlen!" if rnd()>=0.5 else "Tvoi chlen!")

def test(update, context):
    update.message.chat.send_message("test command")

def addCalling204Help(update, context):
    tokens = update.message.text.split(" ")
    if(len(tokens)>1):
        r = context.dispatcher.user_data["r"]
        phrase = " ".join(tokens[1:])
        result = loadList( r, context, "calling204Phrases", phrase )
        update.message.chat.send_message("good: "+str(result))
        context.dispatcher.user_data["calling204Phrases"].add( phrase )
        print("addCalling204Phrases len: " + str(result))
    else:
        update.message.chat.send_message("Invalid args!")
