from pymongo.database import Database
from telegram import Update
from telegram.ext import Application
from telegram.ext import ContextTypes

from src.menus.menu import Menu


async def user_input_echo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.message.from_user is None:
        raise ValueError("Missing message or from_user")
    bot_data = context.application.bot_data
    user_input = update.message.text
    user_id = update.message.from_user.id
    db = bot_data["db"]
    error_logger = bot_data["errorLogger"]
    try:
        context.application.bot_data["echoHandlers"].pop(user_id)
    except KeyError:
        error_logger.error(f"No echoHandler for user {user_id}")
    menu_obj = db.userInput.find_one({"userId": user_id})
    menu = bot_data[menu_obj["menuName"]]
    requested_command = menu_obj.get("requestedCommand")
    if not user_input:
        menu.render_screen(user_id, "emptyInputScreen")
        return
    if not menu_obj:
        error_logger.error(f"Cannot find userId {user_id} in userInput")
        return
    user = update.message.from_user
    user_obj = {
        "link": user.link,
        "name": user.name,
        "fullName": user.full_name,
        "username": user.username,
    }
    db.users.update_one({"userId": user_id}, {"$set": user_obj}, upsert=True)
    db.requestedCommands.update_one(
        {"userId": user_id, "requestedCommand": requested_command},
        {"$set": {"userInput": user_input, "status": 1}},
        upsert=True,
    )
    await context.application.bot.send_message(
        bot_data["adminId"],
        f"User {user_id},{user.full_name},{user.username} requested {requested_command} with input:\n{user_input}",
    )
    menu.render_screen(user_id, "thankYouScreen")


def authorize_add_echo_phrase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query is None:
        raise ValueError("Missing callback_query")
    bot_data = context.application.bot_data
    user_id = update.callback_query.from_user.id
    menu = bot_data["findMenuInContext"](update, context)
    context.application.bot_data["echoHandlers"][user_id] = user_input_echo_handler
    menu_name = menu.render_screen(user_id, "reasonScreen")
    db = bot_data["db"]
    db.userInput.update_one(
        {"user_id": update.callback_query.from_user.id},
        {
            "$set": {
                "menuName": menu_name,
                "status": 0,
                "requestedCommand": "addEchoPhrase",
            }
        },
        upsert=True,
    )


def upsert_to_mongo_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query is None:
        raise ValueError("Missing callback_query")
    bot_data = context.application.bot_data
    user_id = update.callback_query.from_user.id
    menu = bot_data["findMenuInContext"](update, context)
    context.application.bot_data["echoHandlers"][user_id] = user_input_echo_handler
    menu_name = menu.render_screen(user_id, "reasonScreen")
    db = bot_data["db"]
    db.userInput.update_one(
        {"userId": update.callback_query.from_user.id},
        {
            "$set": {
                "menu_name": menu_name,
                "status": 0,
                "requestedCommand": "upsertToMongo",
            }
        },
        upsert=True,
    )


def checkMongoCallbackQuery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query is None:
        raise ValueError("Missing callback_query")
    bot_data = context.application.bot_data
    user_id = update.callback_query.from_user.id
    menu = bot_data["findMenuInContext"](update, context)
    context.application.bot_data["echoHandlers"][user_id] = user_input_echo_handler
    menu_name = menu.render_screen(user_id, "reasonScreen")
    db = bot_data["db"]
    db.userInput.update_one(
        {"userId": user_id},
        {"$set": {"menuName": menu_name, "status": 0, "requestedCommand": "checkMongo"}},
        upsert=True,
    )


def setupRequestAccessMenu(app: Application, db: Database):
    menu = Menu("requestAccess", command="requestAccess", application=app, db=db)
    menu.add_screen_obj(
        {
            "text": "Choose command to request access:",
            "name": "firstScreen",
            "rows": [
                [
                    {
                        "text": "addEchoPhrase",
                        "callbackData": "addEchoPhraseCallbackQuery",
                        "callbackFunction": authorize_add_echo_phrase,
                    },
                    {
                        "text": "checkMongo",
                        "callbackData": "checkMongoCallbackQuery",
                        "callbackFunction": checkMongoCallbackQuery,
                    },
                ],
                [
                    {
                        "text": "upsertToMongo",
                        "callbackData": "upsertToMongo",
                        "callbackFunction": upsert_to_mongo_callback_query,
                    }
                ],
            ],
        }
    )
    menu.add_screen_obj(
        {
            "text": "Second screen",
            "name": "secondScreen",
            "rows": [
                [
                    {
                        "text": "one button",
                        "callbackData": "addEchoPhraseCallbackQuery",
                        "callbackFunction": authorize_add_echo_phrase,
                    }
                ],
            ],
        }
    )
    menu.add_screen_obj({"text": "Thank you for your request", "name": "thankYouScreen"})
    menu.add_screen_obj({"text": "Invalid input(empty)", "name": "emptyInputScreen"})
    menu.add_screen_obj(
        {
            "text": "Why would you need this command?",
            "name": "reasonScreen",
            "callback": "reasonScren",
        }
    )

    # TODO: make less dependent menus on context
    # TODO: future development: add render_screen(..., arguments) -> Button(text+arguments.button1)
    # TODO: send messages to admin if requested command
    # TODO: add dynamic buttons feature addDynamicScreen()
    return menu.build()
