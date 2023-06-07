from telegram import Update
from telegram.ext import CallbackContext, Application
from pymongo.database import Database

from menus.menu import Menu

async def userInputEchoHandler(update : Update, context : CallbackContext):
  bot_data = context.application.bot_data
  userInput = update.message.text
  userId = update.message.from_user.id
  db = bot_data["db"]
  errorLogger = bot_data["errorLogger"]
  try:
      context.application.bot_data["echoHandlers"].pop(userId)
  except KeyError:
      errorLogger.error(f"No echoHandler for user {userId}")
  menuObj = db.userInput.find_one({ "userId" : userId })
  menu = bot_data[menuObj["menuName"]]
  requestedCommand = menuObj.get("requestedCommand")
  if not userInput:
      menu.renderScreen(userId, "emptyInputScreen")
      return
  if not menuObj:
      errorLogger.error(f"Cannot find userId {userId} in userInput")
  user = update.message.from_user
  userObj = { "link" : user.link, "name" : user.name,
      "fullName" : user.full_name, "username" : user.username}
  db.users.update_one({ "userId" : userId },
      { "$set" : userObj }, upsert=True)
  db.requestedCommands.update_one({ "userId" : userId, "requestedCommand" : requestedCommand },
      { "$set" : { "userInput" : userInput, "status" : 1 } }, upsert=True)
  await context.application.bot.send_message(bot_data["adminId"],
      f"User {userId},{user.full_name},{user.username} requested {requestedCommand} with input:\n{userInput}")
  menu.renderScreen(userId, "thankYouScreen")
def authorizeAddEchoPhrase(update, context):
    bot_data = context.application.bot_data
    userId = update.callback_query.from_user.id
    menu = bot_data["findMenuInContext"](update, context)
    context.application.bot_data["echoHandlers"][userId] = userInputEchoHandler
    menuName = menu.renderScreen(userId, "reasonScreen")
    db = bot_data["db"]
    db.userInput.update_one({ "userId" : update.callback_query.from_user.id },
        { "$set" : { "menuName" : menuName, "status" : 0, "requestedCommand" : "addEchoPhrase" }},
        upsert=True)
def upsertToMongoCallbackQuery(update, context):
    bot_data = context.application.bot_data
    userId = update.callback_query.from_user.id
    menu = bot_data["findMenuInContext"](update, context)
    context.application.bot_data["echoHandlers"][userId] = userInputEchoHandler
    menuName = menu.renderScreen(userId, "reasonScreen")
    db = bot_data["db"]
    db.userInput.update_one({ "userId" : update.callback_query.from_user.id },
        { "$set" : { "menuName" : menuName, "status" : 0, "requestedCommand" : "upsertToMongo" }},
        upsert=True)
def checkMongoCallbackQuery(update, context):
    bot_data = context.application.bot_data
    userId = update.callback_query.from_user.id
    menu = bot_data["findMenuInContext"](update, context)
    context.application.bot_data["echoHandlers"][userId] = userInputEchoHandler
    menuName = menu.renderScreen(userId, "reasonScreen")
    db = bot_data["db"]
    db.userInput.update_one({ "userId" : update.callback_query.from_user.id },
        { "$set" : { "menuName" : menuName, "status" : 0, "requestedCommand" : "checkMongo" }},
        upsert=True)

def setupRequestAccessMenu(app : Application, db : Database):
    menu = Menu("requestAccess", command="requestAccess", application=app, db=db)
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

    # TODO: make less dependent menus on context
    # TODO: future development: add renderScreen(..., arguments) -> Button(text+arguments.button1)
    # TODO: send messages to admin if requested command
    # TODO: add dynamic buttons feature addDynamicScreen()
    return menu.build()