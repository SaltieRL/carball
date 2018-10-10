import unittest

from carball.analysis.analysis_manager import AnalysisManager

from carball.tests.utils import run_analysis_test_on_replay, get_specific_replays, get_specific_answers, assertNearlyEqual


class BoostTest(unittest.TestCase):

    def test_1_small_pad_collected(self):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()
            player = proto_game.players[0]
            boost = player.stats.boost
            self.assertEqual(boost.num_small_boosts, 1)
            print(analysis)

        run_analysis_test_on_replay(test, get_specific_replays()["1_SMALL_PAD"])

    def test_1_large_pad_collected(self):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()
            player = proto_game.players[0]
            boost = player.stats.boost
            self.assertEqual(boost.num_large_boosts, 1)
            print(analysis)

        run_analysis_test_on_replay(test, get_specific_replays()["1_LARGE_PAD"])

    def test_0_boost_collected(self):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()
            player = proto_game.players[0]
            boost = player.stats.boost
            self.assertEqual(boost.num_small_boosts, 0)
            self.assertEqual(boost.num_large_boosts, 0)
            print(analysis)

        run_analysis_test_on_replay(test, get_specific_replays()["0_BOOST_COLLECTED"])

    def test_boost_used(self):
        def test(analysis: AnalysisManager, boost_value):
            proto_game = analysis.get_protobuf_data()
            player = proto_game.players[0]
            boost = player.stats.boost
            print("Predicted usage: {}, actual: {}".format(boost.boost_usage, boost_value))
            self.assertAlmostEqual(boost.boost_usage, boost_value, delta=1)
            # self.assertGreater(boost.average_boost_level, 0)

        run_analysis_test_on_replay(test, get_specific_replays()["BOOST_USED"] + get_specific_replays()["0_BOOST_USED"],
                                    answers=get_specific_answers()["BOOST_USED"] +
                                            get_specific_answers()["0_BOOST_USED"])

    def test_boost_feathered(self):
        def test(analysis: AnalysisManager, boost_value):
            proto_game = analysis.get_protobuf_data()
            player = proto_game.players[0]
            boost = player.stats.boost
            print("Predicted usage: {}, actual: {}".format(boost.boost_usage, boost_value))
            assertNearlyEqual(self, boost.boost_usage, boost_value, percent=3)
            # self.assertGreater(boost.average_boost_level, 0)

        run_analysis_test_on_replay(test, get_specific_replays()["BOOST_FEATHERED"],
                                    answers=get_specific_answers()["BOOST_FEATHERED"])

    def test_boost_wasted_collection(self):
        def test(analysis: AnalysisManager, boost_value):
            proto_game = analysis.get_protobuf_data()
            player = proto_game.players[0]
            boost = player.stats.boost
            self.assertAlmostEqual(boost.wasted_collection, boost_value, delta=1)
            # self.assertGreater(boost.average_boost_level, 0)
            print(analysis)

        # run_analysis_test_on_replay(test, get_specific_replays()["BOOST_WASTED_COLLECTION"],
        #                             answers=get_specific_answers()["BOOST_WASTED_COLLECTION"])

    def test_0_used(self):
        def test(analysis: AnalysisManager, boost_value):
            proto_game = analysis.get_protobuf_data()
            player = proto_game.players[0]
            boost = player.stats.boost
            self.assertEqual(boost.boost_usage, boost_value)
            print(analysis)

        run_analysis_test_on_replay(test, get_specific_replays()["0_BOOST_USED"],
                                    answers=get_specific_answers()["0_BOOST_USED"])


if __name__ == '__main__':
    unittest.main()
