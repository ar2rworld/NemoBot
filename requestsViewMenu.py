from telegram import Update
from telegram.ext import CallbackContext, Application
from pymongo.database import Database

from menus.menu import Menu

# menu to view requests and approve/deny them, check TODO 
def setupRequestsViewMenu(app : Application, db : Database):
    menu = Menu("requestsView", command="requestsView", application=app, db=db)
    requestCommands = db.requestedCommands.find({ "status" : 1 })
    menu.addScreenObj({"text" : "List of requests:",
                    "name" : "firstScreen",
                    "rows" : [
                        [ {"text" : f"{r['userId']} {r['requestedCommand']}", "callbackData" : "", "callbackFunction" : lambda : None} for r in requestCommands ]
                    ]})
    menu.build()
