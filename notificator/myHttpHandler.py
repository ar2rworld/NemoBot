from http.server import BaseHTTPRequestHandler
from os import getenv
import json
import socketserver
from typing import Tuple

from notificator.send_notifications import send_notifications
from notificator.xmlParser import xmlParser
from utils.parseUrl import parseUrl

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
  def do_GET(self):
    try:
      self.server.telegramDispatcher.bot.send_message(
        getenv('tg_my_id'),
        f"I got a message from {self.client_address}(might be important):\n{self.requestline}"
      )
      if "?" in self.requestline:
        temp = self.requestline.split("?")[1]
        obj = parseUrl(temp[:temp.index(" ")])
        channelId = obj["hub.topic"].split("channel_id")[1][3:]
        
        find_obj = { "channelId" : channelId}
        if obj.get("hub.verify_token"):
          find_obj["verify_token"] = obj["hub.verify_token"]
        channels = self.server.db["channelsToWatch"].find(find_obj)
        if channels.count():
          self.send_response(200)
          self.end_headers()
          self.wfile.write(bytes(obj["hub.challenge"], "utf-8"))
        else:
          self.send_response(404)
          self.end_headers()
    except Exception as e:
      print(e)
      self.send_error(404, f'Error: {e}')
