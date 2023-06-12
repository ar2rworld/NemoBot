import logging
from http.server import BaseHTTPRequestHandler
from os import getenv
from typing import Tuple, Any

from src.notificator.send_notifications import send_notifications
from src.notificator.server import MyHttpServer
from src.notificator.xmlParser import xmlParser
from src.utils.parseUrl import parseUrl

serverLogger = logging.getLogger("serverLogger")


class Handler(BaseHTTPRequestHandler):
    def __init__(
        self,
        request: Any,
        client_address: Tuple[str, int],
        server: MyHttpServer,
    ) -> None:
        super().__init__(request, client_address, server)
        self.server: MyHttpServer = server

    async def do_POST(self):
        try:
            content_length = int(self.headers["Content-Length"])
            result = xmlParser(self.rfile, content_length)
            await send_notifications(result, self.server.application, self.server.db)

            self.send_response(200)
            self.end_headers()
        except Exception as e:
            serverLogger.error(e)
            self.send_error(404, "Error: %s" % e)

    async def do_GET(self):
        try:
            await self.server.application.bot.send_message(
                getenv("TG_MY_ID"),
                f"I got a message from {self.client_address}(might be important):\n{self.requestline}",
                disable_notification=True,
            )
            if "?" in self.requestline:
                temp = self.requestline.split("?")[1]
                obj = parseUrl(temp[: temp.index(" ")])
                channel_id = obj["hub.topic"].split("channel_id")[1][3:]

                find_obj = {"channelId": channel_id}
                if obj.get("hub.verify_token"):
                    find_obj["verify_token"] = obj["hub.verify_token"]
                channels = self.server.db["channelsToWatch"].find(find_obj)
                count = 0
                for _channel in channels:
                    count += 1
                if count:
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(bytes(obj["hub.challenge"], "utf-8"))
                else:
                    self.send_response(404)
                    self.end_headers()
        except Exception as e:
            serverLogger.error(e)
            self.send_error(404, f"Error: {e}")
