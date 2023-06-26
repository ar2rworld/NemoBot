# NemoBot

## Hello there, just a simple telegram bot friends conversation

### id: nemo4_bot

## Technologies:

<ul>
<li>Python 3.11.4</li>
  <ul>
    <li>redis</li>
    <li>requests-html</li>
    <li>pymongo</li>
    <li>python-telegram-bot</li>
    <li>python-twitter</li>
    <li>requests</li>
    <li>defusedxml</li>
  </ul>
<li>Redis</li>
<li>MongoDB</li>
</ul>

### Run with poetry:
```bash
    poetry env use 3.11.4
    poetry install
    poetry run python NemoBot.py
```

## Commands:

### `/help` - to find out more commands

#### Supports commands for social media posts:

#### API keys required
#### (Not in service for now)
<ul>
  <li>linkedin.com</li>
  <li>vk.com???</li>
  <li>twitter.com</li>
</ul>

### `/my_telegram_id`

#### Sends chat model right from API
# Deploy with docker-compose

### Customize and rename <code>template.env</code> to <code>.env</code> file

### Command
```bash
docker-compose up -d
```

## TODO:
<ul>
    <li>+- Tests</li>
    <li>+ Run linters</li>
    <li>+ Push container to registry</li>
    <li>Deploy to server</li>
    <li>Add alerts</li>
    <li>Add metrics</li>
</ul>

### Linters:
```bash
    pre-commit run -a
    pre-commit run   [hook]
```

### For other commands:

`/help`
