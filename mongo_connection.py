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
