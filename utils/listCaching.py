def loadList(r, context, listName, word=""):
    list = r.lrange(listName, 0, -1)
    word = word.encode("utf-8")
    if(word == b""):
        words=[w.decode("utf-8") for w in list]
        return words
    else:
        if word in list:
            return len(list)
        context.dispatcher.user_data[listName].add(word)
        return r.lpush(listName, word)

def removeFromList(r, context, list, key, n=100) -> int:
    try:
        # if key is not in context skip else remove
        word = word.encode("utf-8")
        if key in context.dispatcher.user_data[list]:
            n = r.lrem(list, n, key)
            context.dispatcher.user_data[list].remove(key)
            return n
        else:
            return 0
    except KeyError:
        return 0