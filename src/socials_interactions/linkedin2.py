import json
import os
from typing import Any
from typing import Union

import requests as req


def linkedin(message: str="") -> str:
    url = "https://api.linkedin.com/v2/ugcPosts"
    linkedin_urn: Union[str, None] = os.getenv("LINKEDIN_URN")
    j = {
        "author": f"urn:li:person:{linkedin_urn}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {"shareCommentary": {"text": message}, "shareMediaCategory": "NONE"}
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }
    headers: Any = {}
    header_env: Union[str, None] = os.getenv("LINKEDIN_HEADERS")
    if header_env:
        headers = json.loads(header_env)
    res = req.post(url, json=j, headers=headers, timeout=5)
    out = "linkedin+" if "id" in json.loads(res.text) else "linkedin-\n" + res.text
    return out
