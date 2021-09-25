import psycopg2
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
      conn = psycopg2.connect(
        dbname = postgres["dbname"],
        user = postgres["user"],
        host = postgres["host"],
        port = postgres["port"],
        password = postgres["password"],
      )
      cursor = conn.cursor()

      print(f"INSERT INTO chats (id, name) VALUES ('%s', '%s') returning id;", (chat_id, chat_name))
      cursor.execute(f"INSERT INTO chats (id, name) VALUES ('%s', %s) returning id;", (chat_id, chat_name))
      id = cursor.fetchone()[0]

      conn.commit()
    except Exception as e:
      print(e)
    finally:
      conn.close()
