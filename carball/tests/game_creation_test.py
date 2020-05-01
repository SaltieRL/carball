from carball.analysis.analysis_manager import AnalysisManager

from carball.json_parser.game import Game
from carball.tests.utils import run_tests_on_list, run_analysis_test_on_replay, get_raw_replays

from carball import decompile_replays


class Test_OverallFunctionality():
    def test_replay_attrs(self):

        def test(replay):
            json_object = decompile_replays.decompile_replay(replay)
            game = Game()
            game.initialize(loaded_json=json_object)
            assert game.game_info.server_name is not None
            assert game.map is not None
            assert game.game_info.match_guid is not None

        run_tests_on_list(test, get_raw_replays()["0_JUMPS"])

    def test_full_replays(self, replay_cache):

        def test(analysis: AnalysisManager):
            assert (analysis.get_protobuf_data() is not None)
            assert(not analysis.get_protobuf_data().game_metadata.is_invalid_analysis)
            for player in analysis.get_protobuf_data().players:
                ratio = (player.stats.positional_tendencies.time_in_front_ball +
                         player.stats.positional_tendencies.time_behind_ball) / player.time_in_game
                assert ratio > 0.99
                # local.assertGreater(player.stats.positional_tendencies.time_in_front_ball, 0)
                # local.assertGreater(player.stats.positional_tendencies.time_behind_ball, 0)
                assert (player.time_in_game > 0)
                assert(player.stats.speed.time_at_slow_speed > 0)
                assert(player.stats.boost.average_boost_level > 0)
                assert(player.stats.boost.wasted_collection > -1)
            json = analysis.get_json_data()
            assert len(json['players']) > 0

        run_analysis_test_on_replay(test, cache=replay_cache)

    def test_unicode_error(self, replay_cache):

        def test(analysis: AnalysisManager):
            assert (analysis.get_protobuf_data() is not None)
            assert (not analysis.get_protobuf_data().game_metadata.is_invalid_analysis)
            for player in analysis.get_protobuf_data().players:
                ratio = (player.stats.positional_tendencies.time_in_front_ball +
                         player.stats.positional_tendencies.time_behind_ball) / player.time_in_game
                assert (ratio > 0.99)
                assert (player.stats.positional_tendencies.time_in_front_ball > 0)
                assert (player.stats.positional_tendencies.time_behind_ball > 0)
                assert (player.time_in_game > 0)
                assert (player.stats.speed.time_at_slow_speed > 0)
                assert (player.stats.boost.average_boost_level > 0)

        run_analysis_test_on_replay(test, get_raw_replays()['UNICODE_ERROR'], cache=replay_cache)
