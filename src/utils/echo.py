import re
from decorators.adminOnly import adminOnly
from mongo_connection import addToCollection

async def echo(update, context):
  echoPhrases = context.application.bot_data["echoPhrases"]
  for phrase in echoPhrases:
    try:
      pattern = phrase["phrase"].lower()
      reg = pattern.replace(' ', r'\s*')
      out = re.match(r".*" + reg + r".*", update.message.text.lower())
      if out:
        await update.message.chat.send_message(phrase["answer"])
    except Exception as e:
      print(e)

@adminOnly
async def addEchoPhrase(update, context):
  message = update.message.text.replace("/addEchoPhrase ", "")
  if '|-|' in message:
    phrase, answer = message.split('|-|')
    obj = {"phrase" : phrase.lower(), "answer" : answer}
    context.application.bot_data["echoPhrases"].append(obj)
    result = addToCollection(context, "echoPhrases", obj, upsertKey="phrase")
    await update.message.chat.send_message(f"Added {result.acknowledged}")
  else:
    await update.message.chat.send_message("'|-|' delimiter is missing")
