import unittest

from carball.analysis.analysis_manager import AnalysisManager

from carball.tests.utils import run_analysis_test_on_replay, get_specific_replays, get_specific_answers, get_raw_replays


class HitTest(unittest.TestCase):

    def test_num_hits_detected(self):

        def test(analysis: AnalysisManager, answer):

            proto_game = analysis.get_protobuf_data()
            hits = proto_game.game_stats.hits
            self.assertEqual(len(hits), answer)
            print(analysis)

        run_analysis_test_on_replay(test, get_specific_replays()["HITS"], get_specific_answers()["HITS"])

    def test_num_kickoff_hits_detected(self):

        def test(analysis: AnalysisManager):

            proto_game = analysis.get_protobuf_data()
            hits = proto_game.game_stats.hits
            kickoff_counter = 0
            for hit in hits:
                if hit.is_kickoff:
                    kickoff_counter += 1
            print(analysis)

            self.assertEqual(kickoff_counter, 3)

        run_analysis_test_on_replay(test, get_raw_replays()["3_KICKOFFS"])


if __name__ == '__main__':
    unittest.main()
