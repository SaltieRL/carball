import unittest

from carball.analysis.analysis_manager import AnalysisManager

from carball.tests.utils import run_analysis_test_on_replay, get_specific_replays


class DBTest(unittest.TestCase):

    def test_0_kickoffs(self):

        def test(analysis: AnalysisManager):

            proto_game = analysis.get_protobuf_data()
            kickoffs = proto_game.game_stats.kickoffs
            self.assertEqual(len(kickoffs), 0)

        run_analysis_test_on_replay(test, get_specific_replays()["KICKOFF_NO_TOUCH"])

    def test_3_kickoffs(self):
        def test(analysis: AnalysisManager):

            proto_game = analysis.get_protobuf_data()
            kickoffs = proto_game.game_stats.kickoffs
            self.assertEqual(len(kickoffs), 3)

        run_analysis_test_on_replay(test, get_specific_replays()["3_KICKOFFS"])


if __name__ == '__main__':
    unittest.main()
