import os
import unittest

from src.my_redis.inmemoryRedis import InmemoryRedis


class TestInmemoryRedis(unittest.TestCase):
    def testBasics(self):
        inr = InmemoryRedis(os.getenv("REDIS_HOST"), os.getenv("REDIS_PORT"))
        pong = inr.ping()
        assert pong is True

        test_list_with_one_item = inr.lpush("testList", "item1")
        assert test_list_with_one_item == 1

        test_list_with_two_items = inr.lpush("testList", "item2")
        assert test_list_with_two_items == 2

        test_list_with_three_items = inr.lpush("testList", "item3")
        assert test_list_with_three_items == 3

        test_lrange_of_two_items = inr.lrange("testList", 0, 1)
        assert test_lrange_of_two_items == ["item1", "item2"]

        test_lrange_of_three_items = inr.lrange("testList", 0, 2)
        assert test_lrange_of_three_items == ["item1", "item2", "item3"]

        test_push_duplicate = inr.lpush("testList", "item2")
        assert test_push_duplicate == 4

        test_rem = inr.lrem("testList", 2, "item2")
        test_list = inr.lrange("testList", 0, -1)
        assert test_list == ["item1", "item3"]
        assert test_rem == 2

        inr.lpush("testList2", "1")
        inr.lpush("testList2", "2")
        inr.lpush("testList2", "3")
        inr.lpush("testList2", "4")
        test_list2 = inr.lrange("testList2", 0, -2)
        assert test_list2 == ["1", "2", "3"]

        test_lrange_of_all_items = inr.lrange("testList2", 0, -1)
        assert test_lrange_of_all_items == ["1", "2", "3", "4"]

    def testEmptyCache(self):
        inr = InmemoryRedis("some_host", "some_port")
        lrange_of_missing_list = inr.lrange("missingList", 0, -1)
        assert lrange_of_missing_list == []

        test_missing_lrem = inr.lrem("missingList", 1, "missingItem")
        assert test_missing_lrem == 0


if __name__ == "__main__":
    unittest.main()
