async def my_telegram_id(update, context):
  await update.message.chat.send_message(str(update.message))