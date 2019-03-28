import unittest

from carball.analysis.analysis_manager import AnalysisManager

from carball.tests.utils import run_analysis_test_on_replay, get_specific_replays, get_raw_replays


class DribbleTests(unittest.TestCase):

    def test_dribble_detection_more_than_zero(self):

        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()
            player = proto_game.players[0]
            self.assertGreater(player.stats.carry_dribbles.total_carries, 0)
            self.assertGreater(player.stats.carry_dribbles.total_carry_time, 0)

        run_analysis_test_on_replay(test, get_specific_replays()["MORE_THAN_ZERO_DRIBBLE"])

    def test_dribble_detection_is_zero(self):

        def test(analysis: AnalysisManager):

            proto_game = analysis.get_protobuf_data()
            kickoffs = proto_game.game_stats.kickoffs
            self.assertEqual(len(kickoffs), 0)

        run_analysis_test_on_replay(test, get_specific_replays()["ZERO_DRIBBLE"])

    def test_3_kickoffs(self):
        def test(analysis: AnalysisManager):

            proto_game = analysis.get_protobuf_data()
            kickoffs = proto_game.game_stats.kickoffs
            self.assertEqual(len(kickoffs), 3)


if __name__ == '__main__':
    unittest.main()
