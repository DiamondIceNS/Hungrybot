import unittest

from game import Game
from player import Player


class TestGame(unittest.TestCase):

    def setUp(self):
        self.g = Game("owner", 0, "title")

    def test_defaults_started(self):
        self.assertFalse(self.g.has_started)

    def test_defaults_day(self):
        self.assertEqual(self.g.day, 1)

    def test_defaults_days_since_last_event(self):
        self.assertEqual(self.g.days_since_last_event, 0)

    def test_addplayer_adds_to_players(self):
        p = Player("name", 1, True)
        self.g.add_player(p)
        self.assertIn("name", self.g.players)
        self.assertEqual(p, self.g.players["name"])

    def test_addplayer_new_player_returns_true(self):
        p = Player("name", 1, True)
        self.assertTrue(self.g.add_player(p))

    def test_addplayer_existing_player_returns_false(self):
        p = Player("name", 1, True)
        self.g.add_player(p)
        self.assertFalse(self.g.add_player(p))

    def test_removeplayer_removes_player(self):
        p = Player("name", 1, True)
        self.g.add_player(p)
        self.g.remove_player("name")
        self.assertNotIn("name", self.g.players)

    def test_removeplayer_existing_player_returns_true(self):
        p = Player("name", 1, True)
        self.g.add_player(p)
        self.assertTrue(self.g.remove_player("name"))

    def test_removeplayer_new_player_returns_true(self):
        p = Player("name", 1, True)
        self.assertFalse(self.g.remove_player("name"))

    def test_startgame_players_alive(self):
        for x in range(10):
            p = Player(str(x), x)
            self.g.add_player(p)
        self.g.start()
        self.assertEqual(self.g.total_players_alive, 10)

    def test_startgame_started(self):
        self.g.add_player(Player("name", 1))
        self.g.add_player(Player("name2", 1))
        self.g.start()
        self.assertTrue(self.g.has_started)

