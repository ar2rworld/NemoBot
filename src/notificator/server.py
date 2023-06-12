import logging
from collections.abc import Callable
from http.server import HTTPServer
from socketserver import BaseRequestHandler
from typing import Tuple

from pymongo.database import Database
from telegram.ext import Application

from src.notificator.myHttpHandler import Handler


class MyHttpServer(HTTPServer):
    def __init__(
        self,
        application,
        db,
        server_address: Tuple[str, int],
        RequestHandlerClass: Callable[..., Handler],
        bind_and_activate: bool = ...,
    ) -> None:
        super().__init__(server_address, RequestHandlerClass, bind_and_activate=bind_and_activate)
        self.application: Application = application
        self.db: Database = db


def run_server(application, db, host, port):
    with MyHttpServer(application, db, (host, int(port)), Handler) as httpd:
        logging.info(f"serving at port: {port}")
        httpd.serve_forever()
