import json
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from os import getenv

from decorators.adminOnly import adminOnly
from access_tokens import mongo

def get_client():
  connection_string = f'mongodb://{getenv("mongo_host")}:{getenv("mongo_port")}'
  client = MongoClient(
    connection_string,
    username=getenv('MONGO_INITDB_ROOT_USERNAME'),
    password=getenv('MONGO_INITDB_ROOT_PASSWORD'))
  try:
    if client[getenv("mongo_dbname")].command('ping'):
      print("mongo connected")
      return client
    else:
      raise Exception('mongo didnot PONG back :/')
      
  except ConnectionFailure as e:
    raise ConnectionFailure

@adminOnly
def check_mongo(update, context):
    try:
        tokens = update.message.text.split(' ')
        dbname = tokens[1]
        collection = tokens[2]
        client = get_client()
        db = client[dbname]
        rows = db[collection].find()
        count = 0
        for i in rows:
            update.message.chat.send_message(str(i))
            count += 1
        if count == 0:
            update.message.chat.send_message("0 rows found")
    
    except Exception as e:
        update.message.chat.send_message(str(e))
        raise e
    finally:
        client.close()

def addToCollection(context, collection, obj, upsertKey=""):
    db = context.dispatcher.user_data["db"]
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
def upsertToMongo(update, context):
    try:
        tokens = update.message.text.split(' ')
        collection = tokens[1]
        message = ' '.join(tokens[2:])
        subTokens = message.split('|-|')
        filter = json.loads(subTokens[0])
        obj = json.loads(subTokens[1])
        db = context.dispatcher.user_data["db"]
        result = db[collection].update_one(filter, obj, upsert=True)
        update.message.chat.send_message(f"{result.acknowledged}")
    except Exception as e:
        update.message.chat.send_message(str(e))