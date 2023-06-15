from os import getenv

from pymongo.database import Database
from telegram.ext import Application


async def send_notifications(video: list[str], application: Application, db: Database) -> None:  # noqa: PLR0912
    if len(video) == 3:
        try:
            link, title, channel_id = video
            channels_to_watch = db["channelsToWatch"]
            channels = channels_to_watch.find({"channelId": channel_id})
            for channel in channels:
                last_video_link = channel.get("lastVideoLink")
                if last_video_link == link:
                    # Do not send notification if the same data were received
                    continue
                channels_to_watch.update_one(channel, {"$set": {"lastVideoLink": link}})

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
                        await application.bot.send_message(channel["chat_id"], text)
                    else:
                        await application.bot.send_message(
                            getenv("TG_MY_ID"),
                            f"Received notification bach did not find any chats to notify:\n{video}",
                        )
                else:
                    await application.bot.send_message(channel["chat_id"], text)
        except KeyError as e:
            application.bot_data["errorLogger"].error(e)
            await application.bot.send_message(getenv("TG_MY_ID"), f"Error: {e}")
    else:
        # something went wrong, error message in (error, )
        error_message = f"Invalid tokens while sending notifications:{video}"
        application.bot_data["errorLogger"].error(error_message)
        await application.bot.send_message(getenv("TG_MY_ID"), error_message)
