import logging
from http.server import HTTPServer
from socketserver import BaseRequestHandler
from typing import Callable, Tuple

from notificator.myHttpHandler import Handler

class myHTTPServer(HTTPServer):
    def __init__(self, telegramDispatcher, db, server_address: Tuple[str, int], RequestHandlerClass: Callable[..., BaseRequestHandler], bind_and_activate: bool = ...) -> None:
        super().__init__(server_address, RequestHandlerClass, bind_and_activate=bind_and_activate)
        self.telegramDispatcher = telegramDispatcher
        self.db = db

def runServer(telegramDispatcher, db, HOST, PORT):

    with myHTTPServer(telegramDispatcher, db, (HOST, int(PORT)), Handler) as httpd:
        logging.info(f"serving at port: {PORT}")
        httpd.serve_forever()
        
#runServer(d)

