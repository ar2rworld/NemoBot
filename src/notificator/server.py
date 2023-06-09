import logging
from collections.abc import Callable
from http.server import HTTPServer
from socketserver import BaseRequestHandler
from typing import Tuple

from src.notificator.myHttpHandler import Handler


class myHTTPServer(HTTPServer):
    def __init__(
        self,
        application,
        db,
        server_address: Tuple[str, int],
        RequestHandlerClass: Callable[..., BaseRequestHandler],
        bind_and_activate: bool = ...,
    ) -> None:
        super().__init__(server_address, RequestHandlerClass, bind_and_activate=bind_and_activate)
        self.application = application
        self.db = db


def runServer(application, db, host, port):
    with myHTTPServer(application, db, (host, int(port)), Handler) as httpd:
        logging.info(f"serving at port: {port}")
        httpd.serve_forever()


# runServer(d)
