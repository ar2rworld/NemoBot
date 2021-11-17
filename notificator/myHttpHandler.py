from http.server import BaseHTTPRequestHandler
import socketserver
from typing import Tuple

from notificator.send_notifications import send_notifications
from notificator.xmlParser import xmlParser

class Handler(BaseHTTPRequestHandler):
  def __init__(self, request: bytes, client_address: Tuple[str, int], server: socketserver.BaseServer) -> None:
      super().__init__(request, client_address, server)
  def do_POST(self):
    try:
      content_length = int(self.headers['Content-Length'])
      result = xmlParser(self.rfile, content_length)
      send_notifications(result, self.server.telegramDispatcher)

      self.send_response(200)
      self.end_headers()
    except Exception as e:
      self.send_error(404, 'Error: %s' % e)
      print(e)

