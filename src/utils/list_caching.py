from redis import Redis
from telegram.ext import ContextTypes


def load_list(r: Redis, list_name: str) -> list[str]:
    word_list: list[bytes] = r.lrange(list_name, 0, -1)
    words = [w.decode("utf-8") for w in word_list]
    return words


def push_word(r: Redis, context: ContextTypes.DEFAULT_TYPE, list_name: str, word: str) -> int:
    word_list = r.lrange(list_name, 0, -1)
    encoded_word = word.encode("utf-8")
    if encoded_word in word_list:
        return len(word_list)
    context.application.bot_data[list_name].add(encoded_word)
    return r.lpush(list_name, encoded_word)


def remove_from_list(r: Redis, context: ContextTypes.DEFAULT_TYPE, list_name: str, key: str, n: int = 100) -> int:
    try:
        # if key is not in context skip else remove
        if key in context.application.bot_data[list_name]:
            n = r.lrem(list_name, n, key)
            context.application.bot_data[list_name].remove(key)
            return n
        return 0
    except KeyError:
        return 0
