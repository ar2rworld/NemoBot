from mongo_connection import addToCollection

def addAlivePhrases(update, context):
    message = update.message.text.replace("/addAlivePhrases ", "")
    delimiter = "|,|"
    n = 0
    if delimiter in message:
        phrases = message.split(delimiter)
        for phrase in phrases:
            if phrase:
                obj = {"phrase" : phrase}
                context.dispatcher.user_data["alivePhrases"].append(obj)
                result = addToCollection(context, "alivePhrases", obj)
                if result.acknowledged:
                    n += 1
    else:
        if message:
            obj = {"phrase" : message}
            context.dispatcher.user_data["alivePhrases"].append(obj)
            result = addToCollection(context, "alivePhrases", obj)
            if result.acknowledged:
                n += 1
    update.message.chat.send_message(f"Phrases added: {n}")