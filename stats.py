from os import getenv

from mongo_connection import get_client
from access_tokens import postgres

def save_conversation(r, message):
  #check if chat id is in redis
  chat_ids = r.lrange("chat_ids", 0, -1)
  chat_id = message['chat']['id']
  chat_title = message['chat']['title']
  username = message['chat']['username']
  chat_name = (chat_title or username).replace("'", "")

  if(str(chat_id).encode('ascii') not in chat_ids):
    r.lpush("chat_ids", chat_id)
    try:
      client = get_client()
      db = client[getenv('mongo_dbname')]

      db['chats'].insert_one({"chat_id": chat_id, "chat_name": chat_name})
    except Exception as e:
      print(f"Error while saving conversation info:\n{e}")
    finally:
      client.close()
