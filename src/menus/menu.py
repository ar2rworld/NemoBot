from collections.abc import Callable
from collections.abc import Coroutine
from typing import Any
from typing import Self

from pymongo.database import Database
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import Update
from telegram.error import TelegramError
from telegram.ext import Application
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler

from src.errors.error_codes import MISSING_CALLBACK_QUERY_OR_DATA
from src.errors.error_codes import MISSING_CALLBACK_QUERY_OR_FROM_USER
from src.errors.error_codes import MISSING_MESSAGE_OR_FROM_USER
from src.menus.errors import MenuError
from src.menus.errors import MissingMenuError
from src.menus.errors import NoScreensMenuError
from src.menus.errors import ScreenMenuError
from src.menus.screen import Screen


class Menu:
    def __init__(self, name: str, command: str, application: Application, db: Database) -> None:
        if "_" in name:
            msg = 'Menu name cannot contain "_", name: "{name}"'
            raise MenuError(msg, self)
        self.screens: dict = {}
        self.name: str = name
        self.application: Application = application
        self.currentScreen: Screen | None = None
        self.firstScreenName: str = ""
        self.currentScreenName = ""
        if not command or " " in command:
            msg = f'Empty command or command contains spaces: "{command}"'
            raise MenuError(msg, self)
        self.command = command
        self.db = db
        self.callback = self.create_callback()

    def add_screen_obj(self, screen_obj: dict) -> None:
        screen_obj["menuName"] = self.name
        if not screen_obj.get("name"):
            msg = f"Screen name is not set:\n{screen_obj}"
            raise ScreenMenuError(msg, self)
        if self.screens.get(screen_obj.get("name")):
            msg = "Screen with name {screen_obj.get('name')} already exists"
            raise ScreenMenuError(msg, self)
        screen = Screen(screen_obj)
        if not self.firstScreenName:
            self.firstScreenName = screen_obj.get("name", "")
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
            if update.message is None or update.message.from_user is None:
                raise ValueError(MISSING_MESSAGE_OR_FROM_USER)
            db = self.db
            if len(self.screens.keys()) == 0:
                raise NoScreensMenuError(self)
            user_id = update.message.from_user.id
            screen = self.screens[self.firstScreenName]
            user_menu = db.userMenus.find_one({"userId": user_id})
            if user_menu:
                try:
                    self.application.bot.delete_message(chat_id=user_id, message_id=user_menu["messageId"])
                except TelegramError as e:
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

    def render_screen(self, chat_id: str, index: str) -> str:
        screen = None
        if isinstance(index, str):
            screen = self.screens[index]
            if screen is None:
                msg = f"Screen with name {index} does not exist"
                raise ScreenMenuError(msg, self)
        self.currentScreen = screen
        self.currentScreenName = screen.name
        user_menu = self.db.userMenus.find_one({"userId": chat_id})
        if user_menu is None:
            msg = "Cannot find user_menu"
            raise ScreenMenuError(msg, self)
        message_id = user_menu["messageId"]
        self.application.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=screen.text,
            reply_markup=screen.markup,
        )
        return self.name

    def build(self) -> Self:
        # setup all handlers and callbacks
        self.application.bot_data["mainLogger"].info(f"Building {self.name}")
        self.application.add_handler(CommandHandler(self.command, self.callback))
        # check if at least one screen exists
        if len(self.screens) == 0:
            msg = "No screens in menu"
            raise MenuError(msg, self)
        # add callbackQueryHandlers from Screens
        for _name, s in self.screens.items():
            for callback, callback_function in s.callbackButtonFunctions.items():
                self.application.bot_data["callbackQueryHandlers"][callback + "_" + self.name] = callback_function
        temp_menu = self.application.bot_data.get(self.name)
        if temp_menu:
            raise MissingMenuError(temp_menu)

        def first_screen_button(update: Update, context: CallbackContext) -> None:
            if update.callback_query is None or update.callback_query.from_user is None:
                raise ValueError(MISSING_CALLBACK_QUERY_OR_FROM_USER)
            bot_data = context.application.bot_data
            bot_data["findMenuInContext"] = find_menu_in_context
            menu = find_menu_in_context(update, context)
            menu.render_screen(str(update.callback_query.from_user.id), self.firstScreenName)

        self.application.bot_data["callbackQueryHandlers"]["firstScreenButton_" + self.name] = first_screen_button

        self.application.bot_data[self.name] = self
        self.application.bot_data["mainLogger"].info(f"Built {self.name}")
        return self

    def render_first_screen(self, chat_id: str) -> None:
        self.render_screen(chat_id, self.firstScreenName)


def find_menu_in_context(update: Update, context: CallbackContext) -> Menu:
    if update.callback_query is None or update.callback_query.data is None:
        raise ValueError(MISSING_CALLBACK_QUERY_OR_DATA)
    menu_name = update.callback_query.data.split("_")[1]
    if menu_name not in context.application.bot_data:
        raise MissingMenuError(menu_name)
    return context.application.bot_data[menu_name]
