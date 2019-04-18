import unittest

from carball.analysis.analysis_manager import AnalysisManager

from carball.tests.utils import run_analysis_test_on_replay, get_raw_replays, get_specific_answers, \
    assertNearlyEqual

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
