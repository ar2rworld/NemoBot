def adminOnly(func):
    def inner(update, x):
        userId = str(update.message.from_user.id)
        user_data = x.dispatcher.user_data
        if userId == user_data['adminId']:
            return func(update, x)
        else:
            db = x.dispatcher.user_data['db']
            user = db.authorizedUsers.find_one({"tg_id" : userId})
            funcName = func.__name__
            if user and funcName in user['authorizedCommands']:
                return func(update, x)
            else:
                update.message.chat.send_message("you not authorized to use this command")
    return inner
