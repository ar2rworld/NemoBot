import twitter

from access_tokens import tokens


twitter_tokens = tokens['twitter']['test0']['ArturBot']

def get_twitter_api():
    api = twitter.Api(consumer_key=twitter_tokens['api_key'],
            consumer_secret=twitter_tokens['api_secret_key'],
            access_token_key=twitter_tokens['access_token'],
            access_token_secret=twitter_tokens['access_token_secret'])
    return api

def twitter_post(message='Hello World from python-twitter!', media=''):
    api = get_twitter_api()
    if api.VerifyCredentials():
        api.PostUpdate(message, media=media)
#twitter_post('testing1 #python #python-twitter', media='https://media.wired.com/photos/5926db217034dc5f91becd6b/master/w_1904,c_limit/so-logo-s.jpg')

    
