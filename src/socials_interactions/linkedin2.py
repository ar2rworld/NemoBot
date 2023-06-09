import json
import os

import requests as req


def linkedin(message=""):
    url = "https://api.linkedin.com/v2/ugcPosts"
    j = json.loads(
        """{
      "author": "urn:li:person:"""
        + os.getenv("LINKEDIN_URN")
        + '''",
      "lifecycleState": "PUBLISHED",
      "specificContent": {
        "com.linkedin.ugc.ShareContent": {
          "shareCommentary": {
            "text": "'''
        + message
        + """"
          },
        "shareMediaCategory": "NONE"
        }
      },
      "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }"""
    )
    headers = json.loads(os.getenv("LINKEDIN_HEADERS"))
    res = req.post(url, json=j, headers=headers)
    out = ""
    out = "linkedin+" if "id" in json.loads(res.text) else "linkedin-\n" + res.text
    return out
