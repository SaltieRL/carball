from carball.tests.utils import get_raw_replays, run_analysis_test_on_replay

from carball.analysis.analysis_manager import AnalysisManager


class Test_Fifties:
    def test_calculate_fifty_fifties(self, replay_cache):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()
            fifties = proto_game.game_stats.fifty_fifties
            # Tuples are (starting frame, ending frame, # hits, # unique players)
            expected_tuples = [
            (173, 177, 4, 2),
            (259, 261, 2, 2),
            (539, 540, 2, 2),
            (1212, 1214, 2, 2),
            (1676, 1679, 2, 2),
            (2261, 2265, 3, 2),
            (2634, 2636, 2, 2),
            (3172, 3174, 3, 2),
            (4132, 4134, 2, 2),
            (4774, 4776, 2, 2),
            (5124, 5127, 2, 2),
            (5224, 5226, 2, 2),
            (6260, 6262, 2, 2),
            (7495, 7496, 2, 2),
            (7916, 7921, 3, 2),
            (8203, 8207, 2, 2),
            (8855, 8857, 3, 2),
            (8906, 8909, 2, 2),
            (9291, 9294, 3, 2),
            (10257, 10259, 2, 2),
            ]
            for i in range(len(fifties)):
                fifty = fifties[i]
                fifty_tuple = (fifty.starting_frame, fifty.ending_frame, len(fifty.hits), len(fifty.players))
                assert(fifty_tuple == expected_tuples[i])

        run_analysis_test_on_replay(test, get_raw_replays()["OCE_RLCS_7_CARS"], cache=replay_cache)
