import unittest

from game import Game
from player import Player


class TestGame(unittest.TestCase):

    def setUp(self):
        self.g = Game("owner", 0, "title")

    def test_defaults_started(self):
        self.assertFalse(self.g.started)

    def test_defaults_day(self):
        self.assertEqual(self.g.day, 1)

    def test_defaults_previous_step_type(self):
        self.assertEqual(self.g.previous_step_type, None)

    def test_defaults_days_since_last_event(self):
        self.assertEqual(self.g.days_since_last_event, 0)

    def test_addplayer_adds_to_players(self):
        p = Player("name", 1, True)
        self.g.add_player(p)
        self.assertIn(p, self.g.players)

    def test_nameexists_does_exist(self):
        name = "The Testing Gremlin"
        p = Player(name, 1)
        self.g.add_player(p)
        self.assertTrue(self.g.name_exists(name))

    def test_nameexists_does_not_exist(self):
        name = "The Testing Gremlin"
        p = Player(name, 1)
        self.g.add_player(p)
        self.assertFalse(self.g.name_exists("name"))

    def test_startgame_players_alive(self):
        players = set()
        for x in range(10):
            p = Player(str(x), x)
            players.add(p)
            self.g.add_player(p)
        self.g.start()
        self.assertTrue(players.issuperset(set(self.g.players_alive)))

    def test_startgame_started(self):
        self.g.add_player(Player("name", 1))
        self.g.add_player(Player("name2", 1))
        self.g.start()
        self.assertTrue(self.g.started)

