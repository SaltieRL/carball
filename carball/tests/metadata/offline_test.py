import unittest

from carball.analysis.analysis_manager import AnalysisManager

from carball.tests.utils import run_analysis_test_on_replay, get_specific_replays


class DBTest(unittest.TestCase):
    def test_offline_replay(self):
        local = self

        def test(analysis: AnalysisManager):
            local.assertIsNotNone(analysis.get_protobuf_data())
            local.assertEqual(False, analysis.get_protobuf_data().game_metadata.is_invalid_analysis)
            game = analysis.get_protobuf_data()
            self.assertEqual(game.game_metadata.match_guid, game.game_metadata.id)

        run_analysis_test_on_replay(test, replay_list=get_specific_replays()["OFFLINE"])
