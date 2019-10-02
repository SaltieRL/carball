import unittest

from carball.analysis.analysis_manager import AnalysisManager

from carball.tests.utils import run_analysis_test_on_replay, get_raw_replays

from carball.generated.api.stats.rumble_pb2 import *


class Test_Rumble():

    def test_pre_item_goals(self, replay_cache):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()

            assert proto_game.game_metadata.goals[0].extra_mode_info.pre_items
            assert not proto_game.game_metadata.goals[1].extra_mode_info.pre_items
            assert proto_game.game_metadata.goals[2].extra_mode_info.pre_items

        run_analysis_test_on_replay(test, get_raw_replays()["RUMBLE_PRE_ITEM_GOALS"], cache=replay_cache)

    def test_item_goals(self, replay_cache):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()
            goals = proto_game.game_metadata.goals

            for i in range(5):
                assert goals[i].extra_mode_info.scored_with_item

            assert (goals[0].extra_mode_info.used_item == GRAVITY_WELL)
            assert (goals[1].extra_mode_info.used_item == BALL_GRAPPLING_HOOK)
            assert (goals[2].extra_mode_info.used_item == STRONG_HIT)
            assert (goals[3].extra_mode_info.used_item == BALL_VELCRO)
            assert (goals[4].extra_mode_info.used_item == BALL_LASSO)

            assert not goals[5].extra_mode_info.scored_with_item

        run_analysis_test_on_replay(test, get_raw_replays()["RUMBLE_ITEM_GOALS"], cache=replay_cache)

    def test_freeze_vs_spike(self, replay_cache):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()

            assert (proto_game.game_stats.rumble_items[1].frame_number_use != -1)

            freeze_stats = next(filter(lambda x: x.item == BALL_FREEZE,
                                       proto_game.players[0].stats.rumble_stats.rumble_items))
            assert (freeze_stats.used == 1)

        run_analysis_test_on_replay(test, get_raw_replays()["RUMBLE_FREEZE_VS_SPIKE"], cache=replay_cache)

    def test_hold_time(self, replay_cache):
        assertions = unittest.TestCase('__init__')

        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()

            spike_stats = next(filter(lambda x: x.item == BALL_VELCRO,
                                      proto_game.players[0].stats.rumble_stats.rumble_items))
            assertions.assertAlmostEqual(spike_stats.average_hold, 11.87916, 5)

            spike_stats = next(filter(lambda x: x.item == BALL_VELCRO,
                                      proto_game.teams[0].stats.rumble_stats.rumble_items))
            assertions.assertAlmostEqual(spike_stats.average_hold, 11.87916, 5)

        run_analysis_test_on_replay(test, get_raw_replays()["RUMBLE_HOLD_TIME"], cache=replay_cache)

    def test_item_count(self, replay_cache):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()

            self.assert_rumble_item_counts(proto_game.players[0].stats.rumble_stats, [
                {'item': BALL_FREEZE, 'used': 1, 'unused': 0},
                {'item': BALL_GRAPPLING_HOOK, 'used': 1, 'unused': 0},
                {'item': BALL_LASSO, 'used': 1, 'unused': 0},
                {'item': BALL_SPRING, 'used': 2, 'unused': 0},
                {'item': BALL_VELCRO, 'used': 0, 'unused': 1},
                {'item': BOOST_OVERRIDE, 'used': 2, 'unused': 0},
                {'item': CAR_SPRING, 'used': 1, 'unused': 1},
                {'item': GRAVITY_WELL, 'used': 2, 'unused': 0},
                {'item': STRONG_HIT, 'used': 2, 'unused': 0},
                {'item': SWAPPER, 'used': 1, 'unused': 0},
                {'item': TORNADO, 'used': 0, 'unused': 0}
            ])

            self.assert_rumble_item_counts(proto_game.players[1].stats.rumble_stats, [
                {'item': BALL_FREEZE, 'used': 2, 'unused': 0},
                {'item': BALL_GRAPPLING_HOOK, 'used': 1, 'unused': 1},
                {'item': BALL_LASSO, 'used': 1, 'unused': 0},
                {'item': BALL_SPRING, 'used': 1, 'unused': 0},
                {'item': BALL_VELCRO, 'used': 0, 'unused': 1},
                {'item': BOOST_OVERRIDE, 'used': 2, 'unused': 0},
                {'item': CAR_SPRING, 'used': 0, 'unused': 1},
                {'item': GRAVITY_WELL, 'used': 2, 'unused': 0},
                {'item': STRONG_HIT, 'used': 1, 'unused': 0},
                {'item': SWAPPER, 'used': 2, 'unused': 0},
                {'item': TORNADO, 'used': 0, 'unused': 1}
            ])

            self.assert_rumble_item_counts(proto_game.players[2].stats.rumble_stats, [
                {'item': BALL_FREEZE, 'used': 1, 'unused': 0},
                {'item': BALL_GRAPPLING_HOOK, 'used': 0, 'unused': 0},
                {'item': BALL_LASSO, 'used': 2, 'unused': 0},
                {'item': BALL_SPRING, 'used': 1, 'unused': 0},
                {'item': BALL_VELCRO, 'used': 1, 'unused': 1},
                {'item': BOOST_OVERRIDE, 'used': 1, 'unused': 1},
                {'item': CAR_SPRING, 'used': 0, 'unused': 0},
                {'item': GRAVITY_WELL, 'used': 2, 'unused': 0},
                {'item': STRONG_HIT, 'used': 2, 'unused': 0},
                {'item': SWAPPER, 'used': 1, 'unused': 1},
                {'item': TORNADO, 'used': 1, 'unused': 0}
            ])

            self.assert_rumble_item_counts(proto_game.players[3].stats.rumble_stats, [
                {'item': BALL_FREEZE, 'used': 0, 'unused': 1},
                {'item': BALL_GRAPPLING_HOOK, 'used': 1, 'unused': 1},
                {'item': BALL_LASSO, 'used': 1, 'unused': 0},
                {'item': BALL_SPRING, 'used': 1, 'unused': 0},
                {'item': BALL_VELCRO, 'used': 1, 'unused': 0},
                {'item': BOOST_OVERRIDE, 'used': 2, 'unused': 0},
                {'item': CAR_SPRING, 'used': 2, 'unused': 0},
                {'item': GRAVITY_WELL, 'used': 1, 'unused': 0},
                {'item': STRONG_HIT, 'used': 1, 'unused': 0},
                {'item': SWAPPER, 'used': 2, 'unused': 0},
                {'item': TORNADO, 'used': 0, 'unused': 0}
            ])

            self.assert_rumble_item_counts(proto_game.players[4].stats.rumble_stats, [
                {'item': BALL_FREEZE, 'used': 2, 'unused': 0},
                {'item': BALL_GRAPPLING_HOOK, 'used': 2, 'unused': 0},
                {'item': BALL_LASSO, 'used': 2, 'unused': 0},
                {'item': BALL_SPRING, 'used': 0, 'unused': 0},
                {'item': BALL_VELCRO, 'used': 1, 'unused': 0},
                {'item': BOOST_OVERRIDE, 'used': 2, 'unused': 0},
                {'item': CAR_SPRING, 'used': 1, 'unused': 0},
                {'item': GRAVITY_WELL, 'used': 2, 'unused': 0},
                {'item': STRONG_HIT, 'used': 1, 'unused': 0},
                {'item': SWAPPER, 'used': 1, 'unused': 1},
                {'item': TORNADO, 'used': 0, 'unused': 0}
            ])

            self.assert_rumble_item_counts(proto_game.players[5].stats.rumble_stats, [
                {'item': BALL_FREEZE, 'used': 2, 'unused': 0},
                {'item': BALL_GRAPPLING_HOOK, 'used': 2, 'unused': 0},
                {'item': BALL_LASSO, 'used': 2, 'unused': 0},
                {'item': BALL_SPRING, 'used': 1, 'unused': 0},
                {'item': BALL_VELCRO, 'used': 1, 'unused': 0},
                {'item': BOOST_OVERRIDE, 'used': 1, 'unused': 0},
                {'item': CAR_SPRING, 'used': 2, 'unused': 0},
                {'item': GRAVITY_WELL, 'used': 0, 'unused': 0},
                {'item': STRONG_HIT, 'used': 2, 'unused': 0},
                {'item': SWAPPER, 'used': 1, 'unused': 1},
                {'item': TORNADO, 'used': 1, 'unused': 0}
            ])

            self.assert_rumble_item_counts(proto_game.teams[0].stats.rumble_stats, [
                {'item': BALL_FREEZE, 'used': 2, 'unused': 1},
                {'item': BALL_GRAPPLING_HOOK, 'used': 2, 'unused': 1},
                {'item': BALL_LASSO, 'used': 4, 'unused': 0},
                {'item': BALL_SPRING, 'used': 4, 'unused': 0},
                {'item': BALL_VELCRO, 'used': 2, 'unused': 2},
                {'item': BOOST_OVERRIDE, 'used': 5, 'unused': 1},
                {'item': CAR_SPRING, 'used': 3, 'unused': 1},
                {'item': GRAVITY_WELL, 'used': 5, 'unused': 0},
                {'item': STRONG_HIT, 'used': 5, 'unused': 0},
                {'item': SWAPPER, 'used': 4, 'unused': 1},
                {'item': TORNADO, 'used': 1, 'unused': 0}
            ])

            self.assert_rumble_item_counts(proto_game.teams[1].stats.rumble_stats, [
                {'item': BALL_FREEZE, 'used': 6, 'unused': 0},
                {'item': BALL_GRAPPLING_HOOK, 'used': 5, 'unused': 1},
                {'item': BALL_LASSO, 'used': 5, 'unused': 0},
                {'item': BALL_SPRING, 'used': 2, 'unused': 0},
                {'item': BALL_VELCRO, 'used': 2, 'unused': 1},
                {'item': BOOST_OVERRIDE, 'used': 5, 'unused': 0},
                {'item': CAR_SPRING, 'used': 3, 'unused': 1},
                {'item': GRAVITY_WELL, 'used': 4, 'unused': 0},
                {'item': STRONG_HIT, 'used': 4, 'unused': 0},
                {'item': SWAPPER, 'used': 4, 'unused': 2},
                {'item': TORNADO, 'used': 1, 'unused': 1}
            ])

        run_analysis_test_on_replay(test, get_raw_replays()["RUMBLE_FULL"], cache=replay_cache)

    def test_item_kickoff(self, replay_cache):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()
            self.assert_rumble_item_counts(proto_game.players[0].stats.rumble_stats, [
                {'item': BALL_FREEZE, 'used': 0, 'unused': 0},
                {'item': BALL_GRAPPLING_HOOK, 'used': 0, 'unused': 0},
                {'item': BALL_LASSO, 'used': 0, 'unused': 0},
                {'item': BALL_SPRING, 'used': 2, 'unused': 0},
                {'item': BALL_VELCRO, 'used': 0, 'unused': 0},
                {'item': BOOST_OVERRIDE, 'used': 0, 'unused': 0},
                {'item': CAR_SPRING, 'used': 0, 'unused': 0},
                {'item': GRAVITY_WELL, 'used': 0, 'unused': 0},
                {'item': STRONG_HIT, 'used': 0, 'unused': 0},
                {'item': SWAPPER, 'used': 0, 'unused': 0},
                {'item': TORNADO, 'used': 0, 'unused': 0}
            ])
        run_analysis_test_on_replay(test, get_raw_replays()["RUMBLE_ITEM_KICKOFF"], cache=replay_cache)

    def assert_rumble_item_counts(self, rumble_stats_proto, expected):
        result_stats = list(map(proto_to_dict, rumble_stats_proto.rumble_items))
        case = unittest.TestCase('__init__')
        case.assertCountEqual(result_stats, expected)


def proto_to_dict(item_proto):
    return {
        'item': item_proto.item,
        'used': item_proto.used,
        'unused': item_proto.unused
    }
