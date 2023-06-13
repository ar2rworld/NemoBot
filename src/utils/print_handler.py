from logging import Logger

from telegram import Update
from telegram.ext import ContextTypes


def print_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    main_logger: Logger = context.bot_data["mainLogger"]
    main_logger.log(msg=update)  # type: ignore reportGeneralTypeIssues
    main_logger.log(msg=context)  # type: ignore reportGeneralTypeIssues
