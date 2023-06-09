def parseUrl(url):
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
            raise Exception("invalid tokens in parseUrl")
    return obj
