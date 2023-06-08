from typing import Callable, Any, Coroutine

from pymongo.database import Database
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import Update
from telegram.ext import Application
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler

from src.menus.screen import Screen


class Menu:
    def __init__(self, name: str, command: str, application: Application, db: Database) -> None:
        if "_" in name:
            raise Exception(f'Menu name cannot contain "_", name: "{name}"')
        self.screens = {}
        self.name = name
        self.application = application
        self.currentScreen = None
        self.firstScreenName = None
        self.currentScreenName = ""
        if command == "" or " " in command:
            raise Exception(f'Empty command or command contains spaces: "{command}"')
        self.command = command
        self.db = db
        self.callback = self.create_callback()

    def add_screen_obj(self, screen_obj: dict) -> None:
        screen_obj["menuName"] = self.name
        if screen_obj.get("name") is None:
            raise Exception(f"Screen name is not set:\n{screen_obj}")
        if self.screens.get(screen_obj.get("name")):
            raise Exception(f"Screen with name {screen_obj.get('name')} already exists")
        screen = Screen(screen_obj)
        if self.firstScreenName is None:
            self.firstScreenName = screen_obj.get("name")
        else:
            first_screen_button = [
                InlineKeyboardButton("go to first screen", callback_data=f"firstScreenButton_{self.name}")
            ]
            screen.rows.append(first_screen_button)
        screen.build()
        self.screens[screen_obj.get("name")] = screen

    def get_screen(self, index: str) -> Screen:
        return self.screens[index]

    def get_markup(self, index: str) -> InlineKeyboardMarkup:
        return self.screens[index].markup

    def __str__(self) -> str:
        return f"Menu: {self.name}\nscreens: {len(self.screens)}\n{[str(i) for i in self.screens]}"

    def create_callback(self) -> Callable[[Update, CallbackContext], Coroutine[Any, Any, None]]:
        async def callback(update: Update, context: CallbackContext) -> None:
            db = self.db
            if len(self.screens.keys()) == 0:
                raise Exception("0 Screens in menu")
            user_id = update.message.from_user.id
            screen = self.screens[self.firstScreenName]
            user_menu = db.userMenus.find_one({"userId": user_id})
            if user_menu:
                try:
                    self.application.bot.delete_message(chat_id=user_id, message_id=user_menu["messageId"])
                except Exception as e:
                    context.application.bot_data["errorLogger"].error(
                        f"Error deleting message (menu: {user_menu}) from {user_id}\n{e}"
                    )
            message = await self.application.bot.send_message(user_id, screen.text, reply_markup=screen.markup)
            # create new menu
            menu_obj = {
                "$set": {
                    "name": self.name,
                    "currentScreenName": self.currentScreenName,
                    "messageId": message.message_id,
                }
            }
            db.userMenus.update_one({"userId": user_id}, menu_obj, upsert=True)

        return callback

    def render_screen(self, chat_id, index: str) -> str:
        screen = None
        if isinstance(index, str):
            screen = self.screens[index]
            if screen is None:
                raise Exception(f"Screen with name {index} does not exist")
        self.currentScreen = screen
        self.currentScreenName = screen.name
        user_menu = self.db.userMenus.find_one({"userId": chat_id})
        message_id = user_menu["messageId"]
        self.application.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=screen.text,
            reply_markup=screen.markup,
        )
        return self.name

    def build(self):
        # setup all handlers and callbacks
        self.application.bot_data["mainLogger"].info(f"Building {self.name}")
        self.application.add_handler(CommandHandler(self.command, self.callback))
        # check if at least one screen exists
        if len(self.screens) == 0:
            raise Exception("No screens in menu")
        # add callbackQueryHandlers from Screens
        for _name, s in self.screens.items():
            for callback, callbackFunction in s.callbackButtonFunctions.items():
                self.application.bot_data["callbackQueryHandlers"][callback + "_" + self.name] = callbackFunction
        temp_menu = self.application.bot_data.get(self.name)
        if temp_menu:
            raise Exception(f"Menu {self.name} already exists")

        def first_screen_button(update: Update, context: CallbackContext) -> None:
            bot_data = context.application.bot_data
            bot_data["findMenuInContext"] = find_menu_in_context
            menu = find_menu_in_context(update, context)
            menu.render_screen(update.callback_query.from_user.id, self.firstScreenName)

        self.application.bot_data["callbackQueryHandlers"]["firstScreenButton_" + self.name] = first_screen_button

        self.application.bot_data[self.name] = self
        self.application.bot_data["mainLogger"].info(f"Built {self.name}")
        return self

    def render_first_screen(self, chat_id) -> None:
        self.render_screen(chat_id, self.firstScreenName)


def find_menu_in_context(update: Update, context: CallbackContext) -> Menu:
    menu_name = update.callback_query.data.split("_")[1]
    if menu_name not in context.application.bot_data:
        raise Exception("Menu does not exist")
    return context.application.bot_data[menu_name]
