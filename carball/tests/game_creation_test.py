import unittest

from ..json_parser.game import Game
from ..tests.utils import test_on_list

from .. import decompile_replays


class DBTest(unittest.TestCase):
    def test_replay_attrs(self):

        def test(replay, file_path):
            json_object = decompile_replays.decompile_replay(replay, file_path)
            game = Game()
            game.initialize(loaded_json=json_object)
            info = game.game_info
            self.assertIsNotNone(game.game_info.server_name)
            self.assertIsNotNone(game.map)
            self.assertIsNotNone(game.game_info.match_guid)

        test_on_list(test)


if __name__ == '__main__':
    unittest.main()
