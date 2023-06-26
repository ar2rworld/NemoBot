import asyncio

from pymongo.database import Database
from telegram.ext import Application

from src.notificator.my_http_handler import Handler
from src.notificator.server import MyHttpServer


def run_server(application: Application, db: Database, host: str, port: int) -> None:
    async def server(application: Application, db: Database, host: str, port: int) -> None:
        with MyHttpServer(application, db, (host, int(port)), Handler) as httpd:
            main_logger = application.bot_data["mainLogger"]
            main_logger.info(f"serving at port: {port}")
            httpd.serve_forever()

    loop = asyncio.new_event_loop()
    loop.create_task(server(application, db, host, port))
    loop.run_forever()
