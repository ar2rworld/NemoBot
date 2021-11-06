from pymongo import MongoClient, results
from pymongo.errors import ConnectionFailure

def get_db(mongo_obj: object):
  connection_string = f'mongodb://{mongo_obj["host"]}:{mongo_obj["port"]}'
  client = MongoClient(connection_string)
  try:
    if client[mongo_obj["dbname"]].command('ping'):
      return client
  except ConnectionFailure:
    print('mongo ConnectionFailure')
    raise ConnectionFailure    

def test_get_db():
  client = get_db({'host': 'localhost', 'port': '27027',  'dbname': 'nemobot'})
  print(client)
#test_get_db()
