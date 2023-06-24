from asyncio import Queue
from os import getenv

from pymongo.database import Database
from telegram.ext import Application


def send_notifications(video: list[str], application: Application, db: Database) -> None:  # noqa: PLR0912
    send_message_queue: Queue = application.bot_data["sendMessageQueue"]
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
                        send_message_queue.put_nowait(
                            {"application": application, "chat_id": channel["chat_id"], "text": text}
                        )
                    else:
                        send_message_queue.put_nowait(
                            {
                                "application": application,
                                "chat_id": getenv("TG_MY_ID"),
                                "text": f"Received notification bach did not find any chats to notify:\n{video}",
                            }
                        )
                else:
                    send_message_queue.put_nowait(
                        {"application": application, "chat_id": channel["chat_id"], "text": text}
                    )
        except KeyError as e:
            application.bot_data["errorLogger"].error(e)
            send_message_queue.put_nowait({"application": application, "chat_id": getenv("TG_MY_ID"), "text": str(e)})
    else:
        # something went wrong, error message in (error, )
        error_message = f"Invalid tokens while sending notifications:{video}"
        application.bot_data["errorLogger"].error(error_message)
        send_message_queue.put_nowait(
            {"application": application, "chat_id": getenv("TG_MY_ID"), "text": error_message}
        )
