import logging
from time import sleep

import requests
from telegram import Update
from telegram.ext import ContextTypes

from src.decorators.adminOnly import admin_only

logging.basicConfig(filename="subscribe.log", filemode="w", level=logging.DEBUG)


async def subscribe(app):
    callbackUrl = app.bot_data["callbackUrl"]
    hubUrl = app.bot_data["hubUrl"]
    tg_my_id = app.bot_data["tg_my_id"]
    db = app.bot_data["db"]

    with open("subscribe.log", mode="w") as f:
        f.write("___very_beginning___")
        f.close()
    while True:
        try:
            # should send HTTP post request to hub url
            logging.info("Starting subscribe")
            channels = db["channelsToWatch"].find()
            out = []
            count = 0
            for channel in channels:
                count += 1
                channel_id = channel["channelId"]
                if channel_id:
                    params = (
                        "/subscribe?hub.mode=subscribe"
                        + f"&hub.callback={callbackUrl}"
                        + "&hub.verify=async"
                        + f"&hub.topic=https://www.youtube.com/xml/feeds/videos.xml?channel_id={channel_id}"
                    )
                    if channel.get("verify_token"):
                        params += f"&hub.verify_token={channel.get('verify_token')}"
                    result = requests.post(
                        url=hubUrl + params,
                        headers={"Content-Type": "application/x-www-form-urlencoded"},
                    )
                    if result.status_code != 202:
                        out.append((channel_id, result.status_code, result.text))
                else:
                    out.append(("", "invalid channelId"))
                    raise Exception("invalid channelId provided for subscribe")
            if len(out) > 0:
                logging.error(f"Number of invalid channels: {len(out)}")
                errors = [f"{str(x)}\n" for x in out]
                await app.bot.send_message(
                    tg_my_id,
                    f"I got some problems while subscribing for following channels:\n{errors}",
                )
            else:
                logging.info(f"Finished subscribe, fetched : {count}")
                await app.bot.send_message(tg_my_id, f"Finished subscribe, fetched : {count}")
                break
        except Exception as e:
            logging.error(e)
        finally:
            sleep(5)


@admin_only
async def subscribe_to_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await subscribe(context.application)
