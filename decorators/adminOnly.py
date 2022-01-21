from os import getenv

def adminOnly(func):
    def inner(update, x):
        if str(update.message.chat.id) == getenv('tg_my_id'):
            return func(update, x)
        else:
            update.message.chat.send_message("you not authorized to use this command")

    return inner
