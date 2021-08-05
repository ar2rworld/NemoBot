import json
import requests as req
from access_tokens import tokens

def linkedin(message=""):
    url = 'https://api.linkedin.com/v2/ugcPosts'
    j=json.loads('''{
      "author": "urn:li:person:''' + tokens['linkedin']['urn'] + '''",
      "lifecycleState": "PUBLISHED",
      "specificContent": {
        "com.linkedin.ugc.ShareContent": {
          "shareCommentary": {
            "text": "''' + message + '''"
          },
        "shareMediaCategory": "NONE"
        }
      },
      "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }''')
    headers = tokens['linkedin']['headers']
    res = req.post(url, json=j, headers=headers)
    out=''
    if 'id' in json.loads(res.text):
      out = 'linkedin+'
    else:
      out='linkedin-\n'+res.text
    return out

