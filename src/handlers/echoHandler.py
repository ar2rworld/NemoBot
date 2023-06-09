from src.handlers.room204 import osuzhdau
from src.handlers.stats import save_conversation
from src.utils.echo import echo


def echoHandler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    echo(update, context)

    save_conversation(context, update.message)

    osuzhdau(update, context)

    bot_data = context.application.bot_data
    try:
        userId = update.message.from_user.id
        bot_data["echoHandlers"][userId](update, context)
    except KeyError:
        pass
