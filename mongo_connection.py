from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from os import getenv

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
      return None
  except ConnectionFailure:
    print('mongo ConnectionFailure')
    raise ConnectionFailure

def check_mongo(update, context):
  try:
    if str(update.message.chat.id) == str(getenv('tg_my_id')):
      tokens = update.message.text.split(' ')
      dbname = tokens[1]
      collection = tokens[2]
      client = get_client(mongo)
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
