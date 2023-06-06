import unittest
import os

from myRedis.inmemoryRedis import InmemoryRedis

class TestInmemoryRedis(unittest.TestCase):
  def testBasics(self):
    inr = InmemoryRedis(os.getenv("redis_host"), os.getenv("redis_port"))
    pong = inr.ping()
    self.assertEqual(pong, True)
    
    testListWithOneItem = inr.lpush("testList", "item1")
    self.assertEqual(testListWithOneItem, ["item1"])

    testListWithTwoItems = inr.lpush("testList", "item2")
    self.assertEqual(testListWithTwoItems, ["item1", "item2"])
    
    testListWithThreeItems = inr.lpush("testList", "item3")
    self.assertEqual(testListWithThreeItems, ["item1", "item2", "item3"])

    testLrangeOfTwoItems = inr.lrange("testList", 0, 1)
    self.assertEqual(testLrangeOfTwoItems, ["item1", "item2"])
    
    testLrangeOfThreeItems = inr.lrange("testList", 0, 2)
    self.assertEqual(testLrangeOfThreeItems, ["item1", "item2", "item3"])

    testPushDuplicate = inr.lpush("testList", "item2")
    self.assertEqual(testPushDuplicate, ["item1", "item2", "item3", "item2"])

    testRem = inr.lrem("testList", 2, "item2")
    testList = inr.lrange("testList", 0, -1)
    self.assertEqual(testList, ["item1", "item3"])
    self.assertEqual(testRem, 2)

    inr.lpush("testList2", "1")
    inr.lpush("testList2", "2")
    inr.lpush("testList2", "3")
    inr.lpush("testList2", "4")
    testList2 = inr.lrange("testList2", 0, -2)
    self.assertEqual(testList2, ["1", "2", "3"])
    
    testLrangeOfAllItems = inr.lrange("testList2", 0, -1)
    self.assertEqual(testLrangeOfAllItems, ["1", "2", "3", "4"])
  
  def testEmptyCache(self):
    inr = InmemoryRedis("somehost", "someport")
    lrangeOfMissingList = inr.lrange("missingList", 0, -1)
    self.assertEqual(lrangeOfMissingList, [])

    testMissingLrem = inr.lrem("missingList", 1, "missingItem")
    self.assertEqual(testMissingLrem, 0)

if __name__ == '__main__':
  unittest.main()
