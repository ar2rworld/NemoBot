from typing import List

class InmemoryRedis:
    def __init__(self, redis_host, redis_port) -> None:
        self.host = redis_host
        self.port = redis_port
        self.dict = {}
    def ping(self) -> bool:
        return self.host != "" and self.port != "" 
    def lrange(self, listName: str, begin: int, end: int) -> List[str]:
        if end == -1:
            end = len(self.dict.get(listName, []))
            return self.dict.get(listName, [])[begin: end]
        return self.dict.get(listName, [])[begin: end+1]
    def lpush(self, listName: str, item: str) -> List[str]:
        if not self.dict.get(listName, []):
            self.dict[listName] = [item]
            return self.dict[listName]
        self.dict[listName].append(item)
        return self.dict[listName]
    def lrem(self, listName: str, nKeysToDelete: int, item: str) -> int:
        i = 0
        for key in self.dict.get(listName, []):
            if key == item and i < nKeysToDelete:
                i += 1
                self.dict[listName].remove(item)
        return i