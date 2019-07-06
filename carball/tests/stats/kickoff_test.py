from carball.analysis.analysis_manager import AnalysisManager

from carball.tests.utils import run_analysis_test_on_replay, get_raw_replays


class Test_Kickoff():

    def test_0_kickoffs(self):

        def test(analysis: AnalysisManager):

            proto_game = analysis.get_protobuf_data()
            kickoffs = proto_game.game_stats.kickoffs
            assert (len(kickoffs) == 0)

        run_analysis_test_on_replay(test, get_raw_replays()["KICKOFF_NO_TOUCH"])

    def test_3_kickoffs(self):
        def test(analysis: AnalysisManager):

            proto_game = analysis.get_protobuf_data()
            kickoffs = proto_game.game_stats.kickoffs
            assert (len(kickoffs) == 3)

        run_analysis_test_on_replay(test, get_raw_replays()["3_KICKOFFS"])

    def test_last_kickoff_no_touch(self):

        def test(analysis: AnalysisManager):

            proto_game = analysis.get_protobuf_data()
            kickoffs = proto_game.game_stats.kickoffs
            assert (len(kickoffs) == 2)

        run_analysis_test_on_replay(test, get_raw_replays()["LAST_KICKOFF_NO_TOUCH"])
