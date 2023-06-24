import asyncio
from asyncio import Queue

from telegram.ext import Application


async def send_message_worker(worker_number: int, queue: Queue) -> None:
    while True:
        obj: dict = await queue.get()

        # send_message
        application: Application | None = obj.get("application")
        chat_id: str = obj.get("chat_id", "")
        text: str = obj.get("text", "")
        delay: int = obj.get("delay", 0.05)
        disable_notification: bool = obj.get("disable_notification", False)
        if not application or not chat_id or not text:
            msg = f"Missing application or chat_id or text in send_message_worker{worker_number}"
            raise ValueError(msg)

        # send message and wait
        await application.bot.send_message(chat_id, text, disable_notification)
        await asyncio.sleep(delay)

        queue.task_done()


def setup_send_message_queue(number_workers: int) -> tuple:
    queue = Queue()
    tasks = []
    for number in range(number_workers):
        tasks.append(asyncio.create_task(send_message_worker(number, queue)))
    return tasks, queue
