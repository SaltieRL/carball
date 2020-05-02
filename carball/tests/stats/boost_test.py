import unittest

from carball.analysis.analysis_manager import AnalysisManager

from carball.tests.utils import run_analysis_test_on_replay, get_specific_replays, get_specific_answers, \
    assertNearlyEqual, get_raw_replays


class Test_Boost():

    def test_1_small_pad_collected(self, replay_cache):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()
            frames = analysis.get_data_frame()
            player = proto_game.players[0]
            boost = player.stats.boost
            assert(boost.num_small_boosts == 1)

        run_analysis_test_on_replay(test, get_specific_replays()["1_SMALL_PAD"], cache=replay_cache)

    def test_1_large_pad_collected(self, replay_cache):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()
            player = proto_game.players[0]
            boost = player.stats.boost
            assert(boost.num_large_boosts == 1)

        run_analysis_test_on_replay(test, get_specific_replays()["1_LARGE_PAD"], cache=replay_cache)

    def test_1_large_pad_1_small_pad_collected(self, replay_cache):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()
            player = proto_game.players[0]
            boost = player.stats.boost
            assert(boost.num_large_boosts == 1)
            assert(boost.num_small_boosts == 1)

        run_analysis_test_on_replay(test, get_raw_replays()["12_AND_100_BOOST_PADS_0_USED"], cache=replay_cache)

    def test_0_boost_collected(self, replay_cache):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()
            player = proto_game.players[0]
            boost = player.stats.boost
            assert(boost.num_small_boosts == 0)
            assert(boost.num_large_boosts == 0)

        run_analysis_test_on_replay(test, get_specific_replays()["0_BOOST_COLLECTED"], cache=replay_cache)

    def test_lots_of_boost_collected(self, replay_cache):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()
            player = proto_game.players[0]
            boost = player.stats.boost
            assert [boost.num_small_boosts, boost.num_large_boosts] == [25, 6]

        run_analysis_test_on_replay(test, get_raw_replays()["6_BIG_25_SMALL"], cache=replay_cache)

    def test_boost_steals(self, replay_cache):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()
            player = proto_game.players[0]
            boost = player.stats.boost
            assert boost.num_stolen_boosts == 2

        run_analysis_test_on_replay(test, get_raw_replays()["6_BIG_25_SMALL"], cache=replay_cache)

    def test_boost_steals_post_goal(self, replay_cache):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()
            player = proto_game.players[0]
            boost = player.stats.boost
            assert [boost.num_small_boosts, boost.num_large_boosts,
                    boost.num_stolen_boosts, boost.boost_usage] == [0, 0, 0, 0]

            player = proto_game.players[1]
            boost = player.stats.boost
            assert [boost.num_large_boosts, boost.num_stolen_boosts] == [3, 3]
            assert boost.boost_usage > 0

        run_analysis_test_on_replay(test, get_raw_replays()["3_STEAL_ORANGE_0_STEAL_BLUE"], cache=replay_cache)

    def test_boost_used(self, replay_cache):
        case = unittest.TestCase('__init__')

        def test(analysis: AnalysisManager, boost_value):
            proto_game = analysis.get_protobuf_data()
            player = proto_game.players[0]
            boost = player.stats.boost
            print("Predicted usage: {}, actual: {}".format(boost.boost_usage, boost_value))
            case.assertAlmostEqual(boost.boost_usage, boost_value, delta=1)
            # self.assertGreater(boost.average_boost_level, 0)

        run_analysis_test_on_replay(test, get_specific_replays()["BOOST_USED"] + get_specific_replays()["0_BOOST_USED"],
                                    answers=get_specific_answers()["BOOST_USED"] +
                                            get_specific_answers()["0_BOOST_USED"], cache=replay_cache)

    def test_boost_feathered(self, replay_cache):
        case = unittest.TestCase('__init__')

        def test(analysis: AnalysisManager, boost_value):
            proto_game = analysis.get_protobuf_data()
            player = proto_game.players[0]
            boost = player.stats.boost
            print("Predicted usage: {}, actual: {}".format(boost.boost_usage, boost_value))
            assertNearlyEqual(case, boost.boost_usage, boost_value, percent=3)
            # self.assertGreater(boost.average_boost_level, 0)

        run_analysis_test_on_replay(test, get_specific_replays()["BOOST_FEATHERED"],
                                    answers=get_specific_answers()["BOOST_FEATHERED"], cache=replay_cache)

    def test_boost_wasted_collection(self, replay_cache):
        case = unittest.TestCase('__init__')

        def test(analysis: AnalysisManager, boost_value):
            proto_game = analysis.get_protobuf_data()
            for index, player in enumerate(proto_game.players):
                wasted_answer = boost_value[index]
                total_wasted = (wasted_answer[0] - (255 - wasted_answer[1])) / 256.0 * 100.0
                boost = player.stats.boost
                case.assertAlmostEqual(boost.wasted_collection, total_wasted, delta=2)

        run_analysis_test_on_replay(test, get_specific_replays()["BOOST_WASTED_COLLECTION"],
                                    answers=get_specific_answers()["BOOST_WASTED_COLLECTION"], cache=replay_cache)

    def test_0_used(self, replay_cache):
        def test(analysis: AnalysisManager, boost_value):
            proto_game = analysis.get_protobuf_data()
            player = proto_game.players[0]
            boost = player.stats.boost
            assert(boost.boost_usage == boost_value)
            print(analysis)

        run_analysis_test_on_replay(test, get_specific_replays()["0_BOOST_USED"],
                                    answers=get_specific_answers()["0_BOOST_USED"], cache=replay_cache)
