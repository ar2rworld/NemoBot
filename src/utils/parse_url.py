def parse_url(url: str) -> dict:
    obj = {}
    tokens = url.split("&")
    for token in tokens:
        temp = token.split("=")
        if len(temp) == 2:
            attr = temp[0]
            value = temp[1]
            obj[attr] = value
        elif len(temp) == 1:
            attr = temp[0]
            obj[attr] = True
        else:
            msg = "invalid tokens in parseUrl"
            raise Exception(msg)
    return obj
