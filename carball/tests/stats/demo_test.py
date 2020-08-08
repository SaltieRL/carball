from carball.tests.utils import get_raw_replays, run_analysis_test_on_replay

from carball.analysis.analysis_manager import AnalysisManager


class Test_Demos:
    def test_calculate_demos_as_bumps_correctly(self, replay_cache):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()
            count_demo_bumps = 0
            for i in proto_game.game_stats.bumps:
                if i.is_demo:
                    count_demo_bumps += 1
            assert count_demo_bumps == 1

        # Skip test cache since this test is calculating intensive events.
        run_analysis_test_on_replay(test, get_raw_replays()["1_DEMO"],
                                    calculate_intensive_events=True)
