from stats import save_conversation
from utils.echo import echo
from room204 import osuzhdau


def echoHandler(update, context):
    echo(update, context)
    
    save_conversation(context, update.message)

    osuzhdau(update, context)
    
    user_data = context.dispatcher.user_data
    try:
        userId = update.message.from_user.id
        user_data["echoHandlers"][userId](update, context)
    except KeyError:
        pass

