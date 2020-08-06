from carball.tests.utils import get_raw_replays, run_analysis_test_on_replay

from carball.analysis.analysis_manager import AnalysisManager


class Test_Bumps:
    def test_calculate_bumps_correctly(self, replay_cache):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()
            count_bumps = 0
            for i in proto_game.game_stats.bumps:
                if not i.is_demo:
                    count_bumps += 1
            assert count_bumps == 3

        run_analysis_test_on_replay(test, get_raw_replays()["3_BUMPS"], cache=replay_cache)
