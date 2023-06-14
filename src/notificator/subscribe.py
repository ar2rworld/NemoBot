import logging
from collections.abc import Coroutine
from time import sleep
from typing import Any

import requests
from pymongo.database import Database
from pymongo.errors import ExecutionTimeout
from telegram import Update
from telegram.ext import Application
from telegram.ext import ContextTypes

from src.decorators.admin_only import admin_only

logging.basicConfig(filename="subscribe.log", filemode="w", level=logging.DEBUG)


async def subscribe(app: Application) -> Coroutine[Any, Any, Any]:
    callback_url: str = app.bot_data["callbackUrl"]
    hub_url: str= app.bot_data["hubUrl"]
    tg_my_id: str = app.bot_data["tg_my_id"]
    db: Database = app.bot_data["db"]


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
                        "/subscribe?hub.mode=subscribe" +
                        + f"&hub.callback={callback_url}"  # type: ignore[reportGeneralTypeIssues]
                        + "&hub.verify=async"
                        + f"&hub.topic=https://www.youtube.com/xml/feeds/videos.xml?channel_id={channel_id}"
                    )
                    if channel.get("verify_token"):
                        params += f"&hub.verify_token={channel.get('verify_token')}"
                    result = requests.post(
                        url=hub_url + params,
                        headers={"Content-Type": "application/x-www-form-urlencoded"},
                        timeout=1
                    )
                    if result.status_code != 202:
                        out.append((channel_id, result.status_code, result.text))
                else:
                    out.append(("", "invalid channelId"))
                    msg = "Missing channelId"
                    raise Exception(msg)
            await check_subscribe_errors(app, count, out, tg_my_id)
        except ValueError as e:
            logging.error(e)
        except TypeError as e:
            logging.error(e)
        except ExecutionTimeout as e:
            logging.error(e)
        finally:
            sleep(5)


async def check_subscribe_errors(app: Application, count: int, out: list[tuple[str]], tg_my_id: str) -> None:
    if len(out) > 0:
        logging.error(f"Number of invalid channels: {len(out)}")
        errors = [f"{x!s}\n" for x in out]
        await app.bot.send_message(
            tg_my_id,
            f"I got some problems while subscribing for following channels:\n{errors}",
        )
    else:
        logging.info(f"Finished subscribe, fetched : {count}")
        await app.bot.send_message(tg_my_id, f"Finished subscribe, fetched : {count}")


@admin_only
async def subscribe_to_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await subscribe(context.application)
