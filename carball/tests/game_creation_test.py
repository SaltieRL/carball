import unittest

from carball.analysis.analysis_manager import AnalysisManager
from carball.analysis.constants.playlist import get_playlist_from_game, get_team_size_from_game

from ..json_parser.game import Game
from ..tests.utils import run_tests_on_list, run_analysis_test_on_replay, get_raw_replays

from .. import decompile_replays


class DBTest(unittest.TestCase):
    def test_replay_attrs(self):
        local = self

        def test(replay, file_path):
            json_object = decompile_replays.decompile_replay(replay, output_path=file_path)
            game = Game()
            game.initialize(loaded_json=json_object)
            info = game.game_info
            local.assertIsNotNone(game.game_info.server_name)
            local.assertIsNotNone(game.map)
            local.assertIsNotNone(game.game_info.match_guid)

        run_tests_on_list(test)

    def test_full_replays(self):
        local = self

        def test(analysis: AnalysisManager):
            local.assertIsNotNone(analysis.get_protobuf_data())
            local.assertEqual(False, analysis.get_protobuf_data().game_metadata.is_invalid_analysis)
            for player in analysis.get_protobuf_data().players:
                ratio = (player.stats.positional_tendencies.time_in_front_ball +
                         player.stats.positional_tendencies.time_behind_ball) / player.time_in_game
                local.assertEqual(True, ratio > 0.99)
                # local.assertGreater(player.stats.positional_tendencies.time_in_front_ball, 0)
                # local.assertGreater(player.stats.positional_tendencies.time_behind_ball, 0)
                local.assertGreater(player.time_in_game, 0)
                local.assertGreater(player.stats.speed.time_at_slow_speed, 0)
                local.assertGreater(player.stats.boost.average_boost_level, 0)
                local.assertGreater(player.stats.boost.wasted_collection, -1)

        run_analysis_test_on_replay(test)

    def test_unicode_error(self):
        local = self

        def test(analysis: AnalysisManager):
            local.assertIsNotNone(analysis.get_protobuf_data())
            local.assertEqual(False, analysis.get_protobuf_data().game_metadata.is_invalid_analysis)
            for player in analysis.get_protobuf_data().players:
                ratio = (player.stats.positional_tendencies.time_in_front_ball +
                         player.stats.positional_tendencies.time_behind_ball) / player.time_in_game
                local.assertEqual(True, ratio > 0.99)
                local.assertGreater(player.stats.positional_tendencies.time_in_front_ball, 0)
                local.assertGreater(player.stats.positional_tendencies.time_behind_ball, 0)
                local.assertGreater(player.time_in_game, 0)
                local.assertGreater(player.stats.speed.time_at_slow_speed, 0)
                local.assertGreater(player.stats.boost.average_boost_level, 0)

        run_analysis_test_on_replay(test, get_raw_replays()['UNICODE_ERROR'])


if __name__ == '__main__':
    unittest.main()
