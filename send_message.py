import os

def send_message(update, context):
  tokens = update.message.text.split(' ')
  if(len(tokens) > 2 and str(update.message.from_user.id) == str(os.getenv('tg_my_id'))):
    context.bot.send_message(
      chat_id = tokens[1],
      text = ' '.join(tokens[ 2: ])
    )
    update.message.chat.send_message('send!')
  else:
    update.message.chat.send_message(f'need some more tokens({len(tokens)}) and you need to have right id')