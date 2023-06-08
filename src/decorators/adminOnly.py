def adminOnly(func):
  async def inner(update, context):
    userId = str(update.message.from_user.id)
    bot_data = context.application.bot_data
    if userId == bot_data['adminId']:
      return await func(update, context)
    else:
      db = context.application.bot_data['db']
      user = db.authorizedUsers.find_one({"tg_id" : userId})
      funcName = func.__name__
      if user and funcName in user['authorizedCommands']:
        return await func(update, context)
      else:
        await update.message.chat.send_message("you not authorized to use this command")
  return inner
