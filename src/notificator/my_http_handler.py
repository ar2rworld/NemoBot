import logging
from http.server import BaseHTTPRequestHandler
from os import getenv
from typing import Any
from xml.etree.ElementTree import ParseError

from pymongo.errors import ExecutionTimeout

from src.notificator.send_notifications import send_notifications
from src.notificator.server import MyHttpServer
from src.notificator.xml_parser import xml_parser
from src.utils.parse_url import parse_url

server_logger = logging.getLogger("server_logger")


class Handler(BaseHTTPRequestHandler):
    def __init__(
        self,
        request: Any,
        client_address: tuple[str, int],
        server: MyHttpServer,
    ) -> None:
        super().__init__(request, client_address, server)
        self.server: MyHttpServer = server

    async def do_POST(self) -> None:  # noqa: N802
        try:
            content_length = int(self.headers["Content-Length"])
            result = xml_parser(self.rfile, content_length)
            await send_notifications(result, self.server.application, self.server.db)

            self.send_response(200)
            self.end_headers()
        except ParseError as e:
            server_logger.error(e)
            self.send_error(404, "Error: %s" % e)

    async def do_GET(self) -> None:  # noqa: N802
        try:
            await self.server.application.bot.send_message(
                getenv("TG_MY_ID"),
                f"I got a message from {self.client_address}(might be important):\n{self.requestline}",
                disable_notification=True,
            )
            if "?" in self.requestline:
                temp = self.requestline.split("?")[1]
                obj = parse_url(temp[: temp.index(" ")])
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
        except ExecutionTimeout as e:
            logging.error(e)
        except KeyError as e:
            server_logger.error(e)
            self.send_error(404, f"Error: {e}")
