from pymongo.database import Database
from telegram.ext import Application

from src.menus.menu import Menu


# menu to view requests and approve/deny them, check TODO
def setupRequestsViewMenu(app: Application, db: Database):
    menu = Menu("requestsView", command="requestsView", application=app, db=db)
    requestCommands = db.requestedCommands.find({"status": 1})
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
                    for r in requestCommands
                ]
            ],
        }
    )
    menu.build()
