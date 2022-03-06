import re

def echo(update, context):
    echoPhrases = context.dispatcher.user_data["echoPhrases"]
    for pattern in echoPhrases.keys():
        reg = pattern.replace(' ', r'\s*')
        out = re.match(r".*" + reg + r".*", update.message.text.lower())
        if out:
            update.message.chat.send_message(echoPhrases[pattern])
