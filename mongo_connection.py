from pymongo import MongoClient

def get_db(mongo_obj: object):
  connection_string = f'mongodb://{mongo_obj["host"]}:{mongo_obj["port"]}'
  return MongoClient(connection_string)[mongo_obj["dbname"]]