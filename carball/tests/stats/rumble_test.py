import unittest

from carball.analysis.analysis_manager import AnalysisManager

from carball.tests.utils import run_analysis_test_on_replay, get_raw_replays, get_specific_answers, \
    assertNearlyEqual


class RumbleTest(unittest.TestCase):

    def test_pre_item_goals(self):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()

            self.assertTrue(proto_game.game_metadata.goals[0].rumble_info.pre_items)
            self.assertFalse(proto_game.game_metadata.goals[1].rumble_info.pre_items)
            self.assertTrue(proto_game.game_metadata.goals[2].rumble_info.pre_items)

        run_analysis_test_on_replay(test, get_raw_replays()["RUMBLE_PRE_ITEM_GOALS"])
