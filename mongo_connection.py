import json
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure
from os import getenv
import logging

from decorators.adminOnly import adminOnly
from access_tokens import mongo

def get_client():
    errorLogger = logging.getLogger("errorLogger")
    connection_string = f'mongodb://{getenv("mongo_host")}:{getenv("mongo_port")}'
    try:
        client = MongoClient(
            connection_string,
            username=getenv('MONGO_INITDB_ROOT_USERNAME'),
            password=getenv('MONGO_INITDB_ROOT_PASSWORD'))
    
        if client[getenv("mongo_dbname")].command('ping'):
            return client
        else:
            raise Exception('mongo didnot PONG back :/')
    except ConnectionFailure as e:
        raise ConnectionFailure
    except Exception as e:
        errorLogger.error(e)
        raise e

@adminOnly
async def checkMongo(update, context):
    try:
        tokens = update.message.text.split(' ')
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
    
    except Exception as e:
        await update.message.chat.send_message(str(e))
        raise e
    finally:
        client.close()

def addToCollection(context, collection, obj, upsertKey=""):
    db = context.application.bot_data["db"]
    try:
        if upsertKey == "":
            return db[collection].insert_one(obj)
        return db[collection].update_one({upsertKey: obj[upsertKey]}, {"$set": obj}, upsert=True)
    except Exception as e:
        raise e

def loadCollection(db, collection):
    try:
        result = db[collection].find()
        r = []
        for i in result:
            r.append(i)
        return r
    except Exception as e:
        raise e

@adminOnly
async def upsertToMongo(update, context):
    try:
        tokens = update.message.text.split(' ')
        collection = tokens[1]
        message = ' '.join(tokens[2:])
        subTokens = message.split('|-|')
        filter = json.loads(subTokens[0])
        obj = json.loads(subTokens[1])
        db = context.application.bot_data["db"]
        result = db[collection].update_one(filter, obj, upsert=True)
        await update.message.chat.send_message(f"{result.acknowledged}")
    except Exception as e:
        await update.message.chat.send_message(str(e))

@adminOnly
async def accessMongo(update, context):
    # /mongo action collectionName json
    try:
        db : Database = context.application.bot_data["db"]
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
        if action == 'insert':
            obj = json.loads(' '.join(tokens[2:]))
            result = db[collection].insert_one(obj)
            await chat.send_message(f"{result.acknowledged}")
        elif action == 'find':
            result = None
            if len(tokens) > 2:
                filter = json.loads(' '.join(tokens[2:]))
                result = db[collection].find(filter)
            else:
                result = db[collection].find()
            c = 0
            output = ""
            for row in result:
                output += str(row) + "\n"
                c += 1
            await chat.send_message(f"{output}{c} rows found")
        elif action == 'update':
            objects = ' '.join(tokens[2:]).split("|-|")
            filter = json.loads(objects[0])
            obj = json.loads(objects[1])
            result = db[collection].update_one(filter, obj)
            await chat.send_message(f"{result.acknowledged}")
        elif action == 'delete':
            filter = json.loads(' '.join(tokens[2:]))
            result = db[collection].delete_one(filter)
            await chat.send_message(f"{result.acknowledged}")
    except Exception as e:
        await update.message.chat.send_message(str(e))
        raise e
