import os

from decorators.adminOnly import adminOnly

@adminOnly
async def send_message(update, context):
  tokens = update.message.text.split(' ')
  if len(tokens) > 2 :
    await context.bot.send_message(
      chat_id = tokens[1],
      text = ' '.join(tokens[ 2: ])
    )
    await update.message.chat.send_message('send!')
  else:
    await update.message.chat.send_message(f'need some more tokens({len(tokens)})')