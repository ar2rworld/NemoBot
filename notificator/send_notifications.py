from typing import Tuple
from os import getenv

from mongo_connection import get_client

def send_notifications(video: Tuple[str,str,str,], telegramDispatcher):
  print(telegramDispatcher)
  if len(video) == 3:
    try:
      link, title, channelId = video
      client = get_client()
      db = client[getenv("mongo_dbname")]
      channelsToWatch = db["channelsToWatch"]
      text = f'\n{title}\n{link}'
      for channel in channelsToWatch.find({"channelId": channelId}):
        telegramDispatcher.bot.send_message(channel.chat_id, channel.get("message")+text)
    except Exception as e:
      print(e)
      telegramDispatcher.bot.send_message(getenv('tg_my_id'), str(e))
    finally:
      client.close()
  else:
    #something went wrong, error message in (error, )
    error_message = f"Invalid tokens while sending notifications:{video}"
    print(error_message)
    telegramDispatcher.bot.send_message(getenv("tg_my_id"), error_message)
      