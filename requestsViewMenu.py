from telegram import Update
from telegram.ext import CallbackContext, Dispatcher
from pymongo.database import Database

from menus.menu import Menu

# menu to view requests and approve/deny them, check TODO 
def setupRequestsViewMenu(dp : Dispatcher, db : Database):
    menu = Menu("requestsView", command="requestsView", dispatcher=dp, db=db)
    requestCommands = db.requestedCommands.find({ "status" : 1 })
    menu.addScreenObj({"text" : "List of requests:",
                    "name" : "firstScreen",
                    "rows" : [
                        [ {"text" : f"{r['userId']} {r['requestedCommand']}", "callbackData" : "", "callbackFunction" : lambda : None} for r in requestCommands ]
                    ]})
    menu.build()
