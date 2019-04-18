import unittest

from carball.analysis.analysis_manager import AnalysisManager

from carball.tests.utils import run_analysis_test_on_replay, get_raw_replays

from carball.generated.api.stats.rumble_pb2 import *


class RumbleTest(unittest.TestCase):

    def test_pre_item_goals(self):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()

            self.assertTrue(proto_game.game_metadata.goals[0].rumble_info.pre_items)
            self.assertFalse(proto_game.game_metadata.goals[1].rumble_info.pre_items)
            self.assertTrue(proto_game.game_metadata.goals[2].rumble_info.pre_items)

        run_analysis_test_on_replay(test, get_raw_replays()["RUMBLE_PRE_ITEM_GOALS"])

    def test_item_goals(self):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()
            goals = proto_game.game_metadata.goals

            for i in range(5):
                self.assertTrue(goals[i].rumble_info.scored_with_item)

            self.assertEqual(goals[0].rumble_info.used_item, GRAVITY_WELL)
            self.assertEqual(goals[1].rumble_info.used_item, BALL_GRAPPLING_HOOK)
            self.assertEqual(goals[2].rumble_info.used_item, STRONG_HIT)
            self.assertEqual(goals[3].rumble_info.used_item, BALL_VELCRO)
            self.assertEqual(goals[4].rumble_info.used_item, BALL_LASSO)

            self.assertFalse(goals[5].rumble_info.scored_with_item)

        run_analysis_test_on_replay(test, get_raw_replays()["RUMBLE_ITEM_GOALS"])

    def test_freeze_vs_spike(self):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()

            self.assertNotEqual(proto_game.game_stats.rumble_items[1].frame_number_use, -1)

            freeze_stats = next(filter(lambda x: x.item == BALL_FREEZE,
                                       proto_game.players[0].stats.rumble_stats.rumble_items))
            self.assertEqual(freeze_stats.used, 1)

        run_analysis_test_on_replay(test, get_raw_replays()["RUMBLE_FREEZE_VS_SPIKE"])

    def test_hold_time(self):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()

            spike_stats = next(filter(lambda x: x.item == BALL_VELCRO,
                                      proto_game.players[0].stats.rumble_stats.rumble_items))
            self.assertAlmostEqual(spike_stats.average_hold, 11.87916, 5)

            spike_stats = next(filter(lambda x: x.item == BALL_VELCRO,
                                      proto_game.teams[0].stats.rumble_stats.rumble_items))
            self.assertAlmostEqual(spike_stats.average_hold, 11.87916, 5)

        run_analysis_test_on_replay(test, get_raw_replays()["RUMBLE_HOLD_TIME"])

    def test_item_count(self):
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

        run_analysis_test_on_replay(test, get_raw_replays()["RUMBLE_FULL"])

    def assert_rumble_item_counts(self, rumble_stats_proto, expected):
        result_stats = list(map(proto_to_dict, rumble_stats_proto.rumble_items))
        self.assertCountEqual(result_stats, expected)


def proto_to_dict(item_proto):
    return {
        'item': item_proto.item,
        'used': item_proto.used,
        'unused': item_proto.unused
    }
