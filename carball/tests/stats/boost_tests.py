import unittest

from carball.analysis.analysis_manager import AnalysisManager

from carball.tests.utils import run_analysis_test_on_replay, get_specific_replays


class DBTest(unittest.TestCase):

    def test_0_boost_used(self):

        def test(analysis: AnalysisManager):

            proto_game = analysis.get_protobuf_data()
            player = proto_game.players[0]
            boost = player.stats.boost
            self.assertEqual(boost.num_small_boosts, 1)
            print(analysis)

        run_analysis_test_on_replay(test, get_specific_replays()["12_BOOST_PAD_0_USED"])


if __name__ == '__main__':
    unittest.main()
