import unittest

from carball.analysis.analysis_manager import AnalysisManager

from carball.tests.utils import run_analysis_test_on_replay, get_specific_replays, get_specific_answers


class HitTest(unittest.TestCase):

    def test_num_hits_detected(self):

        def test(analysis: AnalysisManager, answer):

            proto_game = analysis.get_protobuf_data()
            hits = proto_game.game_stats.hits
            self.assertEqual(len(hits), 1)
            print(analysis)

        run_analysis_test_on_replay(test, get_specific_replays()["HITS"], get_specific_answers()["HITS"])


if __name__ == '__main__':
    unittest.main()
