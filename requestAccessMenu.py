from telegram import Update
from telegram.ext import CallbackContext, Dispatcher
from pymongo.database import Database

from menus.menu import Menu


def userInputEchoHandler(update : Update, context : CallbackContext):
        user_data = context.dispatcher.user_data
        userInput = update.message.text
        userId = update.message.from_user.id
        db = user_data["db"]
        errorLogger = user_data["errorLogger"]
        try:
            context.dispatcher.user_data["echoHandlers"].pop(userId)
        except KeyError:
            errorLogger.error(f"No echoHandler for user {userId}")
        menuObj = db.userInput.find_one({ "userId" : userId })
        menu = user_data[menuObj["menuName"]]
        requestedCommand = menuObj.get("requestedCommand")
        if not userInput:
            menu.renderScreen(userId, "emptyInputScreen")
            return
        if not menuObj:
            errorLogger.error(f"Cannot find userId {userId} in userInput")
        db.requestedCommands.update_one({ "userId" : userId, "requestedCommand" : requestedCommand },
            { "$set" : { "userInput" : userInput, "status" : 1 } }, upsert=True)
        menu.renderScreen(userId, "thankYouScreen")
def authorizeAddEchoPhrase(update, context):
    user_data = context.dispatcher.user_data
    userId = update.callback_query.from_user.id
    menu = user_data["findMenuInContext"](update, context)
    context.dispatcher.user_data["echoHandlers"][userId] = userInputEchoHandler
    menuName = menu.renderScreen(userId, "reasonScreen")
    db = user_data["db"]
    db.userInput.update_one({ "userId" : update.callback_query.from_user.id },
        { "$set" : { "menuName" : menuName, "status" : 0, "requestedCommand" : "addEchoPhrase" }},
        upsert=True)
def upsertToMongoCallbackQuery(update, context):
    user_data = context.dispatcher.user_data
    userId = update.callback_query.from_user.id
    menu = user_data["findMenuInContext"](update, context)
    context.dispatcher.user_data["echoHandlers"][userId] = userInputEchoHandler
    menuName = menu.renderScreen(userId, "reasonScreen")
    db = user_data["db"]
    db.userInput.update_one({ "userId" : update.callback_query.from_user.id },
        { "$set" : { "menuName" : menuName, "status" : 0, "requestedCommand" : "upsertToMongo" }},
        upsert=True)
def checkMongoCallbackQuery(update, context):
    user_data = context.dispatcher.user_data
    userId = update.callback_query.from_user.id
    menu = user_data["findMenuInContext"](update, context)
    context.dispatcher.user_data["echoHandlers"][userId] = userInputEchoHandler
    menuName = menu.renderScreen(userId, "reasonScreen")
    db = user_data["db"]
    db.userInput.update_one({ "userId" : update.callback_query.from_user.id },
        { "$set" : { "menuName" : menuName, "status" : 0, "requestedCommand" : "checkMongo" }},
        upsert=True)

def createRequestAccessMenu(dp : Dispatcher, db : Database):
    menu = Menu("requestAccess", command="requestAccess", dispatcher=dp, db=db)
    menu.addScreenObj({"text" : "Choose command to request access:",
                    "name" : "firstScreen",
                    "rows" : [
                        [
                            {"text" : "addEchoPhrase", "callbackData" : "addEchoPhraseCallbackQuery",
                            "callbackFunction" : authorizeAddEchoPhrase},
                            {"text" : "checkMongo", "callbackData" : "checkMongoCallbackQuery",
                            "callbackFunction" : checkMongoCallbackQuery}
                        ],
                        [
                            {"text" : "upsertToMongo", "callbackData" : "upsertToMongo",
                            "callbackFunction" : upsertToMongoCallbackQuery}
                        ]
                    ]})
    menu.addScreenObj({"text" : "Second screen",
                    "name" : "secondScreen",
                    "rows" : [
                        [{"text" : "one button", "callbackData" : "addEchoPhraseCallbackQuery",
                        "callbackFunction" : authorizeAddEchoPhrase}],
                    ]})
    menu.addScreenObj({"text" : "Thank you for your request",
                    "name" : "thankYouScreen"})
    menu.addScreenObj({"text" : "Invalid input(empty)",
                    "name" : "emptyInputScreen"})
    menu.addScreenObj({"text" : "Why would you need this command?",
                    "name" : "reasonScreen",
                    "callback" : "reasonScren"})

    # TODO: future development: add renderScreen(..., arguments) -> Button(text+arguments.button1)
    return menu.build()