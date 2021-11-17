from http.server import HTTPServer
from socketserver import BaseRequestHandler
from typing import Callable, Tuple

from notificator.myHttpHandler import Handler

class myHTTPServer(HTTPServer):
    def __init__(self, telegramDispatcher, server_address: Tuple[str, int], RequestHandlerClass: Callable[..., BaseRequestHandler], bind_and_activate: bool = ...) -> None:
        super().__init__(server_address, RequestHandlerClass, bind_and_activate=bind_and_activate)
        self.telegramDispatcher = telegramDispatcher

def runServer(telegramDispatcher, PORT):

    with myHTTPServer(telegramDispatcher, ("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()
        
class telegramDispatcherMock():
    def __init__(self, m) -> None:
        self.m = m
    def send_message(self):
        print(self.m)
#d = telegramDispatcherMock('message')
#runServer(d)

    