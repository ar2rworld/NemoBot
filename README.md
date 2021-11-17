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

### `/post -[li][vk][tw] <message>`

#### Supports commands for social media posts:

##### API keys required

<ul>
  <li>linkedin.com</li>
  <li>vk.com</li>
  <li>twitter.com</li>
</ul>

### `/my_telegram_id`

#### Sends chat model right from API

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
postgres = {
    'dbname' : 'dbname',
    'user' : 'user',
    'host' : 'host',
    'password' : 'password',
    'port' : 'port',
}
```

### For other commands:

`/help`
