# NemoBot

## Hello there, just a simple telegram bot friends conversation

### id: nemo4_bot

## Technologies:

<ul>
<li>Python 3.7</li>
  <ul>
    <li>redis</li>
    <li>requests_html</li>
    <li>python-telegram-bot</li>
    <li>python-twitter</li>
    <li>pymongo</li>
  </ul>
<li>Redis</li>
<li>MongoDB</li>
</ul>

## Run

```bash
python NemoBot.py
```

## Commands:

### `/help` - to find out more commands

#### Supports commands for social media posts:

##### API keys required

<ul>
  <li>linkedin.com</li>
  <li>vk.com???</li>
  <li>twitter.com</li>
</ul>

### `/my_telegram_id`

#### Sends chat model right from API

## Deploy with docker-compose

### Add .env file:
```
project_dir=path/to/project
redis_host=redis_host
redis_port=redis_port
mongo_host=mongo_host
mongo_port=mongo_port
mongo_dbname=mongo_dbname
MONGO_INITDB_ROOT_USERNAME=MONGO_INITDB_ROOT_USERNAME
MONGO_INITDB_ROOT_PASSWORD=MONGO_INITDB_ROOT_PASSWORD
NemoBotToken=Telegram_Bot_Token
botGroup=botGroupId
botChannel=botGroupId
tg_my_id=Your_Telegram_Id
notificator_host=notificator_host
notificator_port=notificator_port
callbackUrl=url_to_you_instance.com/add_proxy_pass_to_nginx
hubUrl=https://pubsubhubbub.appspot.com
mongo_volume_path=mongo_volume_path
mongo_initdb_path=mongo_initdb_path
redis_volume_path=redis_volume_path
```

### Command
```bash
docker-compose --env-file .env up --remove-orphans -d
```

### Example of `access_tokens.py`

```python
tokens = {
    'twitter': {
        'test0': {
            'ArturBot':{
                'access_token' : 'access_token',
                'access_token_secret' : 'access_token',
                'api_key' : 'access_token',
                'api_secret_key' : 'access_token',
            }
        }
    },
    'vk': {
        'email' : 'login',
        'pass' : 'password'
    },
    'linkedin': {
        'urn' : 'urn',
        'headers' : {
            'Authorization' : 'Authorization',
            'X-Restli-Protocol-Version' : '2.0.0',
        }
    }
}
```

### For other commands:

`/help`
