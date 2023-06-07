import json
import requests as req
import os

def linkedin(message=""):
    url = 'https://api.linkedin.com/v2/ugcPosts'
    j=json.loads('''{
      "author": "urn:li:person:''' + os.getenv('linkedin_urn') + '''",
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
    headers = os.getenv('linkedin_headers')
    res = req.post(url, json=j, headers=headers)
    out=''
    if 'id' in json.loads(res.text):
      out = 'linkedin+'
    else:
      out='linkedin-\n'+res.text
    return out

