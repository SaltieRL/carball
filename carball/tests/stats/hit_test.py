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

    def test_num_shots_detected(self):

        def test(analysis: AnalysisManager, answer):

            proto_game = analysis.get_protobuf_data()
            hits = proto_game.game_stats.hits
            shot_counter = 0
            for hit in hits:
                if hit.shot:
                    shot_counter += 1

            self.assertEqual(shot_counter, answer)

        run_analysis_test_on_replay(test, get_specific_replays()["SHOTS"], get_specific_answers()["SHOTS"])

    def test_num_passes_detected(self):

        def test(analysis: AnalysisManager, answer):

            proto_game = analysis.get_protobuf_data()
            hits = proto_game.game_stats.hits
            pass_counter = 0
            for hit in hits:
                if hit.pass_:
                    pass_counter += 1

            self.assertEqual(pass_counter, answer)

        run_analysis_test_on_replay(test, get_specific_replays()["PASSES"], get_specific_answers()["PASSES"])

    def test_num_aerials_detected(self):

        def test(analysis: AnalysisManager, answer):

            proto_game = analysis.get_protobuf_data()
            hits = proto_game.game_stats.hits
            aerial_counter = 0
            for hit in hits:
                if hit.aerial:
                    aerial_counter += 1

            self.assertEqual(aerial_counter, answer)

        run_analysis_test_on_replay(test, get_specific_replays()["AERIALS"], get_specific_answers()["AERIALS"])


if __name__ == '__main__':
    unittest.main()
