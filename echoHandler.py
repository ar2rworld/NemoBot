from stats import save_conversation
from utils.echo import echo
from room204 import osuzhdau


def echoHandler(update, context):
    echo(update, context)
    
    save_conversation(context, update.message)

    osuzhdau(update, context)
