import os

import twitter


def get_twitter_api():
    api = twitter.Api(
        consumer_key=os.getenv("API_KEY"),
        consumer_secret=os.getenv("API_SECRET_KEY"),
        access_token_key=os.getenv("ACCESS_TOKEN"),
        access_token_secret=os.getenv("ACCESS_TOKEN_SECRET"),
    )
    return api


def twitter_post(message="Hello World from python-twitter!", media=""):
    api = get_twitter_api()
    if api.VerifyCredentials():
        api.PostUpdate(message, media=media)
