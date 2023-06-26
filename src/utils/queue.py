import asyncio
from asyncio import Queue
from threading import Thread

from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.error import TimedOut
from telegram.ext import Application
from telegram.ext import ContextTypes


async def send_message_worker(context: ContextTypes.DEFAULT_TYPE) -> None:
    worker_number: int = context.bot_data["workerNumber"] or 1
    queue: Queue = context.bot_data["sendMessageQueue"]

    async def work(worker_queue: Queue) -> None:
        obj: dict = await worker_queue.get()

        # send_message
        application: Application | None = obj.get("application")
        chat_id: str = obj.get("chat_id", "")
        text: str = obj.get("text", "")
        delay: int = obj.get("delay", 0.05)
        disable_notification: bool = obj.get("disable_notification", False)
        parse_mode: str = obj.get("parse_mode", ParseMode.HTML)
        if not application or not chat_id or not text:
            msg = f"Missing application or chat_id or text in send_message_worker{worker_number}"
            raise ValueError(msg)

        # send message and wait
        try:
            await application.bot.send_message(
                chat_id, text, disable_notification=disable_notification, parse_mode=parse_mode
            )
        except BadRequest as e:
            application.bot_data["errorLogger"].error(f"send_message_worker BadRequest with message: {e}")
        except TimedOut as e:
            application.bot_data["errorLogger"].error(f"send_message_worker BadRequest with message: {e}")
        await asyncio.sleep(delay)

        worker_queue.task_done()

    tasks = []
    for _ in range(worker_number):
        tasks.append(asyncio.create_task(work(queue)))

    await asyncio.gather(*tasks, return_exceptions=True)


def setup_send_message_queue() -> tuple[Queue, Thread]:
    queue = Queue()

    async def run_queue_coroutine(q: Queue) -> None:
        queue_loop = asyncio.new_event_loop()
        task = asyncio.create_task(q.join())
        queue_loop.run_until_complete(task)

    th = Thread(target=run_queue_coroutine, args=(queue,))
    return queue, th
