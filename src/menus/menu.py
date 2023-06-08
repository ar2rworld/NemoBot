from typing import Callable, List
from menus.screen import Screen
from telegram import InlineKeyboardButton, Message, InlineKeyboardMarkup, MessageId, Update
from telegram.ext import Application, CallbackContext, CommandHandler

from pymongo.database import Database

class Menu:
  def __init__(self, name : str, command : str, application : Application, db : Database) -> None:
    if "_" in name:
      raise Exception(f"Menu name cannot contain \"_\", name: \"{name}\"")
    self.screens = {}
    self.name = name
    self.application = application
    self.currentScreen = None
    self.firstScreenName = None
    self.currentScreenName = ""
    if command == "" or " " in command:
      raise Exception(f"Empty command or command contains spaces: \"{command}\"")
    self.command = command
    self.db = db
    self.callback : Callable[[Update, CallbackContext], None] = self.createCallback()
  def addScreenObj(self, screenObj : dict) -> None:
    screenObj["menuName"] = self.name
    if screenObj.get("name") is None:
      raise Exception(f"Screen name is not set:\n{screenObj}")
    if self.screens.get(screenObj.get("name")):
      raise Exception(f"Screen with name {screenObj.get('name')} already exists")
    screen = Screen(screenObj)
    if self.firstScreenName is None:
      self.firstScreenName = screenObj.get("name")
    else:
      firstScreenButton = [InlineKeyboardButton("go to first screen", callback_data=f"firstScreenButton_{self.name}")]
      screen.rows.append(firstScreenButton)
    screen.build()
    self.screens[screenObj.get("name")] = screen
  def getScreen(self, index : str) -> Screen:
    return self.screens[index]
  def getMarkup(self, index : str) -> InlineKeyboardMarkup:
    return self.screens[index].markup
  def __str__(self) -> str:
    return f"Menu: {self.name}\nscreens: {len(self.screens)}\n{[str(i) for i in self.screens]}"
  def createCallback(self) -> Callable[[Update, CallbackContext], None]:
    async def callback(update : Update, context : CallbackContext) -> None:
      db = self.db
      if len(self.screens.keys()) == 0:
        raise Exception(f"0 Screens in menu")
      userId = update.message.from_user.id
      screen = self.screens[self.firstScreenName]
      userMenu = db.userMenus.find_one({"userId": userId})
      if userMenu:
        try:
          self.application.bot.delete_message(chat_id=userId, message_id=userMenu["messageId"])
        except Exception as e:
          context.application.bot_data["errorLogger"].error(f"Error deleting message (menu: {userMenu}) from {userId}\n{e}")
      message = await self.application.bot.send_message(userId, screen.text, reply_markup=screen.markup)
      # create new menu
      menuObj = {"$set" : {"name" : self.name, "currentScreenName" : self.currentScreenName, "messageId" : message.message_id}}
      db.userMenus.update_one({"userId" : userId}, menuObj, upsert=True)
    return callback
  def renderScreen(self, chatId, index : str) -> None:
    screen = None
    if isinstance(index, str):
      screen = self.screens[index]
      if screen is None:
        raise Exception(f"Screen with name {index} does not exist")
    self.currentScreen = screen
    self.currentScreenName = screen.name
    userMenu = self.db.userMenus.find_one({ "userId" : chatId })
    messageId = userMenu["messageId"]
    self.application.bot.edit_message_text(chat_id=chatId, message_id=messageId, text=screen.text, reply_markup=screen.markup)
    return self.name
  def build(self):
      # setup all handlers and callbacks
      self.application.bot_data["mainLogger"].info(f"Building {self.name}")
      self.application.add_handler(CommandHandler(self.command, self.callback))
      # check if at least one screen exists
      if len(self.screens) == 0:
          raise Exception("No screens in menu")
      # add callbackQueryHandlers from Screens
      for name, s in self.screens.items():
          for callback, callbackFunction in s.callbackButtonFunctions.items():
              self.application.bot_data["callbackQueryHandlers"][callback + "_" + self.name] = callbackFunction
      tempMenu = self.application.bot_data.get(self.name)
      if tempMenu:
          raise Exception(f"Menu {self.name} already exists")
      
      def firstScreenButton(update : Update, context : CallbackContext) -> None:
          bot_data = context.application.bot_data
          bot_data["findMenuInContext"] = findMenuInContext
          menu = findMenuInContext(update, context)
          menu.renderScreen(update.callback_query.from_user.id, self.firstScreenName)
      self.application.bot_data["callbackQueryHandlers"]["firstScreenButton_" + self.name] = firstScreenButton

      self.application.bot_data[self.name] = self
      self.application.bot_data["mainLogger"].info(f"Built {self.name}")
      return self
  def renderFirstScreen(self, chatId) -> None:
      self.renderScreen(chatId, self.firstScreenName)

def findMenuInContext(update : Update, context : CallbackContext) -> Menu:
  menuName = update.callback_query.data.split("_")[1]
  if menuName not in context.application.bot_data:
    raise Exception(f"Menu does not exist")
  return context.application.bot_data[menuName]
