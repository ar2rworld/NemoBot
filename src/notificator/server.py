from collections.abc import Callable
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

from pymongo.database import Database
from telegram.ext import Application


class MyHttpServer(HTTPServer):
    def __init__(
        self,
        application: Application,
        db: Database,
        server_address: tuple[str, int],
        request_handler_class: Callable[..., BaseHTTPRequestHandler],
    ) -> None:
        super().__init__(server_address, request_handler_class)
        self.application: Application = application
        self.db: Database = db
