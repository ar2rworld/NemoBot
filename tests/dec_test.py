# I have no idea how to test python but i need this function to be tested
# import make_post from socials
import unittest

from src.socials_interactions.socials import dec


class TestDec(unittest.TestCase):
    def test_dec(self) -> None:
        params = "a=1&b=123&c=a1@><)- 1_"
        res = dec(params)
        assert res["a"] == "1", 'missing value "a"'
        assert res["b"] == "123", 'missing value "b"'
        assert res["c"] == "a1@><)- 1_", 'missing value "c"'
