import unittest

from hungergames import HungerGames
from enums import ErrorCode


class TestErrors(unittest.TestCase):

    def setUp(self):
        self.hg = HungerGames()

    def tearDown(self):
        self.hg.end_game(0, 0)

    # Test New Game

    def test_newgame_gameexists(self):
        self.hg.new_game(0, 0, "owner", "title")
        self.assertEqual(self.hg.new_game(0, None, None, "Title"), ErrorCode.GAME_EXISTS)

    # Test Add Player

    def test_addplayer_nogame(self):
        self.assertEqual(self.hg.add_player(0, "test"), ErrorCode.NO_GAME)

    def test_addplayer_gamestarted(self):
        self.hg.new_game(0, 0, "owner", "title")
        self.hg.add_player(0, "test1")
        self.hg.add_player(0, "test2")
        self.hg.start_game(0, 0, "h$")
        self.assertEqual(self.hg.add_player(0, "test3"), ErrorCode.GAME_STARTED)

    def test_addplayer_gamefull(self):
        self.hg.new_game(0, 0, "owner", "title")
        for i in range(24):
            self.hg.add_player(0, str(i))
        self.assertEqual(self.hg.add_player(0, "test"), ErrorCode.GAME_FULL)

    def test_addplayer_charlimit(self):
        self.hg.new_game(0, 0, "owner", "title")
        self.assertEqual(self.hg.add_player(0, "person with 33character long name"), ErrorCode.CHAR_LIMIT)

    def test_addplayer_playerexists(self):
        self.hg.new_game(0, 0, "owner", "title")
        self.hg.add_player(0, "test")
        self.assertEqual(self.hg.add_player(0, "test"), ErrorCode.PLAYER_EXISTS)

    # Test Pad Players

    def test_padplayers_nogame(self):
        self.assertEqual(self.hg.pad_players(0, "melee"), ErrorCode.NO_GAME)

    def test_padplayers_gamestarted(self):
        self.hg.new_game(0, 0, "owner", "title")
        self.hg.add_player(0, "test1")
        self.hg.add_player(0, "test2")
        self.hg.start_game(0, 0, "h$")
        self.assertEqual(self.hg.pad_players(0, "melee"), ErrorCode.GAME_STARTED)

    def test_padplayers_gamefull(self):
        self.hg.new_game(0, 0, "owner", "title")
        for i in range(24):
            self.hg.add_player(0, str(i))
        self.assertEqual(self.hg.pad_players(0, "melee"), ErrorCode.GAME_FULL)

    def test_padplayers_invalidgroup(self):
        self.hg.new_game(0, 0, "owner", "title")
        self.assertEqual(self.hg.pad_players(0, None), ErrorCode.INVALID_GROUP)

    # Test Status

    def test_status_nogame(self):
        self.assertEqual(self.hg.status(0), ErrorCode.NO_GAME)

    # Test Start Game

    def test_startgame_nogame(self):
        self.assertEqual(self.hg.start_game(0, 0, "h$"), ErrorCode.NO_GAME)

    def test_startgame_notowner(self):
        self.hg.new_game(0, 0, "owner", "title")
        self.assertEqual(self.hg.start_game(0, 1, "h$"), ErrorCode.NOT_OWNER)

    def test_startgame_gamestarted(self):
        self.hg.new_game(0, 0, "owner", "title")
        self.hg.add_player(0, "test1")
        self.hg.add_player(0, "test2")
        self.hg.start_game(0, 0, "h$")
        self.assertEqual(self.hg.start_game(0, 0, "h$"), ErrorCode.GAME_STARTED)

    def test_startgame_notenoughplayers_0(self):
        self.hg.new_game(0, 0, "owner", "title")
        self.assertEqual(self.hg.start_game(0, 0, "h$"), ErrorCode.NOT_ENOUGH_PLAYERS)

    def test_startgame_notenoughplayers_1(self):
        self.hg.new_game(0, 0, "owner", "title")
        self.hg.add_player(0, "test")
        self.assertEqual(self.hg.start_game(0, 0, "h$"), ErrorCode.NOT_ENOUGH_PLAYERS)

    # Test End Game

    def test_endgame_nogame(self):
        self.assertEqual(self.hg.end_game(0, 0), ErrorCode.NO_GAME)

    def test_endgame_notowner(self):
        self.hg.new_game(0, 0, "owner", "title")
        self.assertEqual(self.hg.end_game(0, 1), ErrorCode.NOT_OWNER)

    # Test Step

    def test_step_nogame(self):
        self.assertEqual(self.hg.step(0, 0), ErrorCode.NO_GAME)

    def test_step_notowner(self):
        self.hg.new_game(0, 0, "owner", "title")
        self.hg.add_player(0, "test1")
        self.hg.add_player(0, "test2")
        self.hg.start_game(0, 0, "h$")
        self.assertEqual(self.hg.step(0, 1), ErrorCode.NOT_OWNER)

    def test_step_gamenotstarted(self):
        self.hg.new_game(0, 0, "owner", "title")
        self.assertEqual(self.hg.step(0, 0), ErrorCode.GAME_NOT_STARTED)


if __name__ == '__main__':
    unittest.main()
