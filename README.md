# NemoBot

## Hello there, just a simple telegram bot friends conversation

### id: nemo4_bot

## Technologies:

<ul>
<li>Python 3.11</li>
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
PROJECT_DIR=path/to/project
REDIS_HOST=redis_host
REDIS_PORT=redis_port
MONGO_HOST=mongo_host
MONGO_PORT=mongo_port
MONGO_DBNAME=mongo_dbname
MONGO_INITDB_ROOT_USERNAME=MONGO_INITDB_ROOT_USERNAME
MONGO_INITDB_ROOT_PASSWORD=MONGO_INITDB_ROOT_PASSWORD
NEMOBOTTOKEN=Telegram_Bot_Token
BOTGROUP=botGroupId
BOTCHANNEL=botGroupId
TG_MY_ID=Your_Telegram_Id
NOTIFICATOR_HOST=notificator_host
NOTIFICATOR_PORT=notificator_port
CALLBACKURL=url_to_you_instance.com/add_proxy_pass_to_nginx
HUBURL=https://pubsubhubbub.appspot.com
MONGOVOLUMEPATH=mongo_volume_path
MONGOINITDBPATH=mongo_initdb_path
REDISVOLUMEPATH=redis_volume_path
LINKEDIN_HEADERS=someJsonHeadersStructure
LINKEDIN_URN=someLinkedinUrn
VK_EMAIL=vkEmailOrPhone
VK_PASS=vkPassword
```

### Command
```bash
docker-compose --env-file .env up --remove-orphans -d
```

## TODO:
<ul>
    <li>Tests</li>
    <li>Run linters</li>
    <li>Push container to registry</li>
    <li>Deploy to server</li>
    <li>Add alerts</li>
    <li>Add metrics</li>
</ul>

### Linters:
```bash
    pre-commit run -a
    pre-commit run   [hook]
```

### Run with poetry:
```bash
    poetry run python NemoBot.py
```

### For other commands:

`/help`
