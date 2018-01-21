import unittest

from hungergames import HungerGames
from enums import ErrorCode


class TestHungerGames(unittest.TestCase):

    def setUp(self):
        self.hg = HungerGames()

    def tearDown(self):
        self.hg.end_game(0, 0)

