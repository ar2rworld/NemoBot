import os

import twitter

def get_twitter_api():
    api = twitter.Api(consumer_key= os.getenv('api_key'),
            consumer_secret= os.getenv('api_secret_key'),
            access_token_key= os.getenv('access_token'),
            access_token_secret= os.getenv('access_token_secret'))
    return api

def twitter_post(message='Hello World from python-twitter!', media=''):
    api = get_twitter_api()
    if api.VerifyCredentials():
        api.PostUpdate(message, media=media)
