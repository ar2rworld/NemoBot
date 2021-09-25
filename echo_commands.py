def my_telegram_id(update, context):
  update.message.chat.send_message(str(update.message))