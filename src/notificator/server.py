from collections.abc import Callable
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from typing import Tuple

from pymongo.database import Database
from telegram.ext import Application


class MyHttpServer(HTTPServer):
    def __init__(
        self,
        application: Application,
        db: Database,
        server_address: Tuple[str, int],
        request_handler_class: Callable[..., BaseHTTPRequestHandler],
        bind_and_activate: bool = ...,
    ) -> None:
        super().__init__(server_address, request_handler_class, bind_and_activate=bind_and_activate)
        self.application: Application = application
        self.db: Database = db
