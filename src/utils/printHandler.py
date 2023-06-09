from telegram import Update
from telegram.ext import ContextTypes


def printHandler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update)
    print(context)
