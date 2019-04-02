import unittest

from carball.analysis.analysis_manager import AnalysisManager

from carball.tests.utils import run_analysis_test_on_replay, get_specific_replays, get_raw_replays


class DribbleTests(unittest.TestCase):

    def test_dribble_detection_more_than_zero(self):

        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()
            carries = proto_game.game_stats.ball_carries
            self.assertGreater(len(carries), 0)
            player = proto_game.players[0]
            self.assertGreater(player.stats.ball_carries.total_carries, 0)
            self.assertGreater(player.stats.ball_carries.total_carry_time, 0)

        run_analysis_test_on_replay(test, get_specific_replays()["MORE_THAN_ZERO_DRIBBLE"])

    def test_dribble_detection_is_zero(self):

        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()
            carries = proto_game.game_stats.ball_carries
            self.assertEqual(len(carries), 0)

        run_analysis_test_on_replay(test, get_specific_replays()["ZERO_DRIBBLE"])

    def test_total_dribble_time(self):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()
            player = proto_game.players[0]
            print(player)
            self.assertAlmostEqual(player.stats.ball_carries.total_carry_time, 235, delta=1)

        run_analysis_test_on_replay(test, get_raw_replays()["SKYBOT_DRIBBLE_INFO"])


if __name__ == '__main__':
    unittest.main()
