class InmemoryRedis:
    def __init__(self, redis_host: str, redis_port: int) -> None:
        self.host: str = redis_host
        self.port: int = redis_port
        self.dict = {}

    def ping(self) -> bool:
        return not self.host and not self.port

    def lrange(self, list_name: str, begin: int, end: int) -> list[str]:
        if end == -1:
            end = len(self.dict.get(list_name, []))
            return self.dict.get(list_name, [])[begin:end]
        return self.dict.get(list_name, [])[begin : end + 1]

    def lpush(self, list_name: str, item: str) -> int:
        if not self.dict.get(list_name, []):
            self.dict[list_name] = [item]
            return len(self.dict[list_name])
        self.dict[list_name].append(item)
        return len(self.dict[list_name])

    def lrem(self, list_name: str, n_keys_to_delete: int, item: str) -> int:
        i = 0
        for key in self.dict.get(list_name, []):
            if key == item and i < n_keys_to_delete:
                i += 1
                self.dict[list_name].remove(item)
        return i
