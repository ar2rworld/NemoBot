from telegram import Update
from telegram.ext import ContextTypes


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.chat is None:
        msg = "Missing message or chat"
        raise ValueError(msg)
    await update.message.chat.send_message("start command")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.chat is None:
        msg = "Missing message or chat"
        raise ValueError(msg)
    await update.message.chat.send_message(
        """
/postaviat
/tvoichlen
/osuzhdat <bad word>
/osuzhdat -p <bad phrase>
/osuzhdat -a
/neosuzhdat <bad word>
/neosuzhdat -p <bad phrase>
/my_telegram_id
/addCalling204Help <helping phrase>
add \"calling204\" when joking
/addAlivePhrases <phrase> [|,|<phrase>|,|<phrase>...]
Admin commands:
    /checkMongo <dbName> <tableName>
    /upsertToMongo <tableName> <json>
    /post
    /addEchoPhrase <phrase>|-|<answer>
    /subscribeToChannels
    /accessMongo [showTables] <insert|find|update|delete> <collectionName> [filter|<filter|-|json>]
    """
    )


async def test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.chat is None:
        msg = "Missing message or chat"
        raise ValueError(msg)
    await update.message.chat.send_message("yeah, this is a test command")


async def error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    error_logger = context.application.bot_data["errorLogger"]
    error_logger.error(update)
    return await error_logger.error(context.error)
