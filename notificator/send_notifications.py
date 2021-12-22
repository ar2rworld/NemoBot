from typing import Tuple
from os import getenv

def send_notifications(video: Tuple[str,str,str,], telegramDispatcher, db):
  if len(video) == 3:
    try:
      link, title, channelId = video
      channelsToWatch = db["channelsToWatch"]
      channels = channelsToWatch.find({"channelId": channelId})
      for channel in channels:
        lastVideoLink = channel.get("lastVideoLink")
        if lastVideoLink == link:
          continue
        channelsToWatch.update_one(channel, {
          "$set" : {
            "lastVideoLink" : link
          }
        })

        text = f"\n{title}\n{link}"
        if channel.get("message"):
          text = f"{channel.get('message')}\n{text}"
        if channel.get("keywords"):
          send = False
          for keyword in channel.get("keywords"):
            if keyword in title:
              send = True
              break
          if send:
            telegramDispatcher.bot.send_message(channel["chat_id"], text)
          else:
            telegramDispatcher.bot.send_message(getenv("tg_my_id"),
              f"Received notification bach didnot find any chats to notify:\n{video}")
        else:
          telegramDispatcher.bot.send_message(channel["chat_id"], text)
    except Exception as e:
      print(e)
      telegramDispatcher.bot.send_message(getenv('tg_my_id'), f"Error: {e}")
  else:
    #something went wrong, error message in (error, )
    error_message = f"Invalid tokens while sending notifications:{video}"
    print(error_message)
    telegramDispatcher.bot.send_message(getenv("tg_my_id"), error_message)
      
