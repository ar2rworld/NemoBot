from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os

from access_tokens import mongo

def get_db(mongo_obj: object):
  connection_string = f'mongodb://{mongo_obj["host"]}:{mongo_obj["port"]}'
  client = MongoClient(
    connection_string,
    username=os.getenv('MONGO_INITDB_ROOT_USERNAME'),
    password=os.getenv('MONGO_INITDB_ROOT_PASSWORD'))
  try:
    if client[mongo_obj["dbname"]].command('ping'):
      print("mongo connected")
      return client
  except ConnectionFailure:
    print('mongo ConnectionFailure')
    raise ConnectionFailure    

def check_mongo(update, context):
  try:
    if str(update.message.chat.id) == str(os.getenv('tg_my_id')):
      tokens = update.message.text.split(' ')
      dbname = tokens[1]
      collection = tokens[2]
      client = get_db(mongo)
      db = client[dbname]
      rows = db[collection].find()
      for i in rows:
        update.message.chat.send_message(str(i))
      if not rows.count():
          update.message.chat.send_message("0 rows found")
    else:
      update.message.chat.send_message('not my owner')

  except Exception as e:
    update.message.chat.send_message(str(e))
  finally:
    client.close()
