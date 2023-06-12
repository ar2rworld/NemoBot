import json
import logging
from os import getenv

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure
from telegram import Update
from telegram.ext import ContextTypes

from src.decorators.adminOnly import admin_only


def get_client():
    error_logger = logging.getLogger("errorLogger")

    mongo_host = getenv("MONGO_HOST")
    mongo_port = getenv("MONGO_PORT")
    mongo_dbname = getenv("MONGO_DBNAME")
    if mongo_host is None or mongo_port is None or mongo_dbname is None:
        raise ValueError("Missing MONGO_HOST or MONGO_PORT or MONGO_DBNAME is the environment")
    connection_string = f'mongodb://{getenv("MONGO_HOST")}:{getenv("MONGO_PORT")}'
    try:
        client = MongoClient(
            connection_string,
            username=getenv("MONGO_INITDB_ROOT_USERNAME"),
            password=getenv("MONGO_INITDB_ROOT_PASSWORD"),
        )

        if client[mongo_dbname].command("ping"):
            return client
        else:
            raise Exception("mongo did not PONG back :/")
    except ConnectionFailure:
        raise ConnectionFailure
    except Exception as e:
        error_logger.error(e)
        raise e


@admin_only
async def check_mongo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.message.text is None:
        raise ValueError("Missing message or text")
    try:
        tokens = update.message.text.split(" ")
        dbname = tokens[1]
        collection = tokens[2]
        client = get_client()
        db = client[dbname]
        rows = db[collection].find()
        count = 0
        for i in rows:
            await update.message.chat.send_message(str(i))
            count += 1
        if count == 0:
            await update.message.chat.send_message("0 rows found")
        client.close()
    except Exception as e:
        await update.message.chat.send_message(str(e))
        raise e


def add_to_collection(context: ContextTypes.DEFAULT_TYPE, collection: str, obj: dict, upsert_key: str = ""):
    db = context.application.bot_data["db"]
    try:
        if upsert_key == "":
            return db[collection].insert_one(obj)
        return db[collection].update_one({upsert_key: obj[upsert_key]}, {"$set": obj}, upsert=True)
    except Exception as e:
        raise e


def load_collection(db, collection):
    try:
        result = db[collection].find()
        r = []
        for i in result:
            r.append(i)
        return r
    except Exception as e:
        raise e


@admin_only
async def upsert_to_mongo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.message.text is None:
        raise ValueError("Missing message or text")
    try:
        tokens = update.message.text.split(" ")
        collection = tokens[1]
        message = " ".join(tokens[2:])
        sub_tokens = message.split("|-|")
        filter_parameter = json.loads(sub_tokens[0])
        obj = json.loads(sub_tokens[1])
        db = context.application.bot_data["db"]
        result = db[collection].update_one(filter_parameter, obj, upsert=True)
        await update.message.chat.send_message(f"{result.acknowledged}")
    except Exception as e:
        await update.message.chat.send_message(str(e))


@admin_only
async def accessMongo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # /mongo action collectionName json
    if update.message is None or update.message.text is None:
        raise ValueError("Missing message or text")
    try:
        db: Database = context.application.bot_data["db"]
        message = update.message.text.replace("/accessMongo ", "")
        chat = update.message.chat
        if message == "showTables":
            result = db.list_collection_names()
            await chat.send_message(f"{result}")
            return
        tokens = message.split(" ")
        if len(tokens) < 2:
            raise Exception("Not enough arguments")
        action = tokens[0]
        collection = tokens[1]
        if action == "insert":
            obj = json.loads(" ".join(tokens[2:]))
            result = db[collection].insert_one(obj)
            await chat.send_message(f"{result.acknowledged}")
        elif action == "find":
            result = None
            if len(tokens) > 2:
                filter_separator = json.loads(" ".join(tokens[2:]))
                result = db[collection].find(filter_separator)
            else:
                result = db[collection].find()
            c = 0
            output = ""
            for row in result:
                output += str(row) + "\n"
                c += 1
            await chat.send_message(f"{output}{c} rows found")
        elif action == "update":
            objects = " ".join(tokens[2:]).split("|-|")
            filter_separator = json.loads(objects[0])
            obj = json.loads(objects[1])
            result = db[collection].update_one(filter_separator, obj)
            await chat.send_message(f"{result.acknowledged}")
        elif action == "delete":
            filter_separator = json.loads(" ".join(tokens[2:]))
            result = db[collection].delete_one(filter_separator)
            await chat.send_message(f"{result.acknowledged}")
    except Exception as e:
        await update.message.chat.send_message(str(e))
        raise e
