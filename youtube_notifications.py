from datetime import date, datetime
import json
import requests
from datetime import datetime

import access_tokens
from mongo_connection import get_db

def composeMessage(video: object):
  title = video['snippet']['title']
  id = video['id']['videoId']
  return f'{title}\nhttps://www.youtube.com/watch?v={id}'


def watchChannels(context):
  db = get_db(access_tokens.mongo)
  base_uri = 'https://youtube.googleapis.com/youtube/v3/search?part=snippet'
  key = access_tokens.tokens['youtube']['key']
  channelsToWatch = db['channelsToWatch']

  for i in channelsToWatch.find():
    channelId = i['channelId']
    publishedAfter = i.get('publishedAfter', str(datetime.now().isoformat())+'Z')
    url = f'{base_uri}&channelId={channelId}&key={key}&order=date&maxResults=10&publishedAfter={publishedAfter}'
    print(url)
    result = requests.get(url)
    data = json.loads(result.text)['items']
    videosToNotify = []

    if i.get('keywords'):
      for v in data:
        for keyword in i['keywords']:
            if keyword in v['snippet']['title'] or keyword in v['snippet']['description']:
              videosToNotify.append(v)
    else:
      videosToNotify = data
    
    if len(videosToNotify) and videosToNotify[0]['id']['videoId'] != i.get('lastVideoId'):
      print('have some videos', videosToNotify[0], i.get('lastVideoId'))
      context.bot.sendMessage(i['chat_id'], '\n'.join([composeMessage(v) for v in videosToNotify]))
    else:
      #print('nothing to post')
      pass

    if len(data):
      channelsToWatch.update_one(
        { '_id' : i['_id']},
        {
          '$set' :{
            'lastVideoId': data[0]['id']['videoId'],
            'publishedAfter' : data[0]['snippet']['publishedAt'],
          }
        })

def setupJobQueue(dp):
  dp.job_queue.run_repeating(callback=watchChannels, interval=60)

  

#setupJobQueue()