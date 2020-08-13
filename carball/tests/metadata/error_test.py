import unittest

from carball.analysis.analysis_manager import AnalysisManager

from carball.tests.utils import run_analysis_test_on_replay, get_specific_replays


class DBTest(unittest.TestCase):
    def test_error_replay(self):
        local = self

        def test(analysis: AnalysisManager):
            local.assertIsNone(analysis.get_protobuf_data())
            local.assertEqual(False, analysis.get_protobuf_data().game_metadata.is_invalid_analysis)

        try:
            run_analysis_test_on_replay(test, replay_list=get_specific_replays()["BROKEN_REPLAYS"])
        except FileNotFoundError as e:
            self.assertIsInstance(e, FileNotFoundError)
