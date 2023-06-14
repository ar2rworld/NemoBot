from pymongo.database import Database
from telegram.ext import Application

from src.menus.menu import Menu


# menu to view requests and approve/deny them, check TODO
def setup_requests_view_menu(app: Application, db: Database) -> None:
    menu = Menu("requestsView", command="requestsView", application=app, db=db)
    request_commands = db.requestedCommands.find({"status": 1})
    menu.add_screen_obj(
        {
            "text": "List of requests:",
            "name": "firstScreen",
            "rows": [
                [
                    {
                        "text": f"{r['userId']} {r['requestedCommand']}",
                        "callbackData": "",
                        "callbackFunction": lambda: None,
                    }
                    for r in request_commands
                ]
            ],
        }
    )
    menu.build()
