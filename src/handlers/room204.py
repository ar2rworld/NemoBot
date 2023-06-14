import re
from logging import Logger
from random import random as rnd

from telegram import Update
from telegram.ext import ContextTypes

from src.errors.error_codes import MISSING_MESSAGE_OR_CHAT
from src.errors.error_codes import MISSING_MESSAGE_OR_CHAT_OR_TEXT
from src.utils.list_caching import load_list
from src.utils.list_caching import push_word
from src.utils.list_caching import remove_from_list


async def kolonka(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.chat is None:
        raise ValueError(MISSING_MESSAGE_OR_CHAT)
    await update.message.chat.send_message("Postaviat!" if rnd() >= 0.5 else "Net, ne postaviat.")


async def osuzhdau(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  # noqa: C901
    if update.message is None or update.message.chat is None or update.message.text is None:
        raise ValueError(MISSING_MESSAGE_OR_CHAT_OR_TEXT)
    calling204_phrases = context.application.bot_data["calling204Phrases"]
    mat = context.application.bot_data["mat"]
    error_logger: Logger = context.application.bot_data["errorLogger"]
    osuzhdat_n = 0
    try:
        message: str = update.message.text.lower()
        for m in mat:
            try:
                if re.match(r".*" + str(m).lower() + ".*", message):
                    osuzhdat_n += 1
            except ValueError as e:
                error_logger.error(e)

        if osuzhdat_n != 0:
            dots = "." * osuzhdat_n if osuzhdat_n > 0 else 1
            await update.message.chat.send_message(f"ocyждaю {dots}")
        if re.match(r".*calling204.*", message):
            if len(calling204_phrases) == 0:
                context.application.bot_data["calling204Phrases"] = {"Haha, man, your are the best!"}
            n = int(rnd() * len(calling204_phrases))
            phrase = ""
            for i, key in enumerate(calling204_phrases):
                if n == i:
                    phrase = key
                    break
            await update.message.chat.send_message(phrase)
    except ValueError as e:
        error_logger.error(f"Exception occurred: {e}")


async def osuzhdat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.chat is None or update.message.text is None:
        raise ValueError(MISSING_MESSAGE_OR_CHAT_OR_TEXT)
    tokens = update.message.text.split(" ")
    r = context.application.bot_data["r"]

    if len(tokens) == 2 and tokens[1] != "-p" and tokens[1] != "-a":
        n = push_word(r, context, "mat", tokens[1])
        await update.message.chat.send_message("Got it! Let's make community better together!(words : " + str(n) + ")")
    elif len(tokens) > 2 and tokens[1] == "-p":
        n = push_word(r, context, "mat", " ".join(tokens[2:]).lower())
        await update.message.chat.send_message("Got your phrase, let's osuzhdat together!(" + str(n) + ")")
    elif len(tokens) == 2 and tokens[1] == "-a":
        await update.message.chat.send_message(
            "I don't wanna see this words:\n" + str(context.application.bot_data["mat"])
        )
    else:
        await update.message.chat.send_message("Plz, i need the word u don't wanna hear/see")


async def neosuzhdat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.chat is None or update.message.text is None:
        raise ValueError(MISSING_MESSAGE_OR_CHAT_OR_TEXT)
    r = context.application.bot_data["r"]
    load_list(r, "mat")
    tokens = update.message.text.split(" ")

    if len(tokens) == 2 and tokens[1] != "-p":
        n = remove_from_list(r, context, "mat", tokens[1])
        await update.message.chat.send_message("I hope that you making a wise decision, words deleted: " + str(n) + ".")
    elif len(tokens) > 2 and tokens[1] == "-p":
        n = remove_from_list(r, context, "mat", " ".join(tokens[2:]))
        await update.message.chat.send_message(
            "I know you are a brave man, hope that you making a wise decision, phrases deleted: " + str(n) + "."
        )
    else:
        await update.message.chat.send_message("I can't understan you, check my /help=(")
    context.application.bot_data["mat"] = load_list(r, "mat")


async def tvoichlen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.chat is None:
        raise ValueError(MISSING_MESSAGE_OR_CHAT)
    await update.message.chat.send_message("Moi chlen!" if rnd() >= 0.5 else "Tvoi chlen!")


async def add_calling_204_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.chat is None or update.message.text is None:
        raise ValueError(MISSING_MESSAGE_OR_CHAT_OR_TEXT)
    tokens = update.message.text.split(" ")
    if len(tokens) > 1:
        r = context.application.bot_data["r"]
        phrase = " ".join(tokens[1:])
        result = push_word(r, context, "calling204Phrases", phrase)
        await update.message.chat.send_message("good: " + str(result))
        context.application.bot_data["calling204Phrases"].add(phrase)
    else:
        await update.message.chat.send_message("Invalid args!")
