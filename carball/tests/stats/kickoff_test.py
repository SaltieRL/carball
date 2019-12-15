from carball.analysis.analysis_manager import AnalysisManager

from carball.tests.utils import run_analysis_test_on_replay, get_raw_replays


class Test_Kickoff():

    def test_0_kickoffs(self):
        def test(analysis: AnalysisManager):

            proto_game = analysis.get_protobuf_data()
            kickoffs = proto_game.game_stats.kickoffs
            assert (len(kickoffs) == 0)

            first_player = proto_game.players[0].stats
            kickoff_stats = first_player.kickoff_stats
            assert kickoff_stats.total_kickoffs == 0

        run_analysis_test_on_replay(test, get_raw_replays()["KICKOFF_NO_TOUCH"])

    def test_no_one_for_kickoffs(self):
        def test(analysis: AnalysisManager):

            proto_game = analysis.get_protobuf_data()
            kickoffs = proto_game.game_stats.kickoffs
            assert (len(kickoffs) == 1)

        run_analysis_test_on_replay(test, get_raw_replays()["NO_ONE_FOR_KICKOFF"])

    def test_no_one_for_weird_kickoffs(self):
        def test(analysis: AnalysisManager):

            proto_game = analysis.get_protobuf_data()
            kickoffs = proto_game.game_stats.kickoffs
            assert (len(kickoffs) == 3)

            first_player = proto_game.players[0].stats
            kickoff_stats = first_player.kickoff_stats
            assert kickoff_stats.total_kickoffs == 3

        run_analysis_test_on_replay(test, get_raw_replays()["WEIRD_KICKOFFS"])

    def test_3_kickoffs(self):
        def test(analysis: AnalysisManager):

            proto_game = analysis.get_protobuf_data()
            kickoffs = proto_game.game_stats.kickoffs
            assert (len(kickoffs) == 3)

            first_player = proto_game.players[0].stats
            kickoff_stats = first_player.kickoff_stats
            assert kickoff_stats.num_time_first_touch == 3
            assert kickoff_stats.num_time_go_to_ball == 3
            assert kickoff_stats.total_kickoffs == 3
            for i in range(len(kickoffs)):
                kickoff = proto_game.game_stats.kickoff_stats[i]
                player = kickoff.touch.players[0]
                start_left = player.start_position.pos_x > 0
                assert player.start_left == start_left
        run_analysis_test_on_replay(test, get_raw_replays()["3_KICKOFFS"])

    def test_last_kickoff_no_touch(self):

        def test(analysis: AnalysisManager):

            proto_game = analysis.get_protobuf_data()
            kickoffs = proto_game.game_stats.kickoffs
            assert (len(kickoffs) == 2)

            first_player = proto_game.players[0].stats
            kickoff_stats = first_player.kickoff_stats
            assert kickoff_stats.total_kickoffs == 2

        run_analysis_test_on_replay(test, get_raw_replays()["LAST_KICKOFF_NO_TOUCH"])

    def test_all_kickoffs(self):
        def test(analysis: AnalysisManager):

            proto_game = analysis.get_protobuf_data()
            kickoffs = proto_game.game_stats.kickoffs
            assert (len(kickoffs) == 5)
            first_player = proto_game.players[0].stats
            kickoff_stats = first_player.kickoff_stats
            assert kickoff_stats.num_time_first_touch == 0
            assert kickoff_stats.num_time_go_to_ball == 2
            assert kickoff_stats.num_time_boost == 1
            assert kickoff_stats.num_time_cheat == 1
            assert kickoff_stats.num_time_defend == 1
            assert kickoff_stats.total_kickoffs == 5

            second_player_stats = proto_game.players[1].stats.kickoff_stats
            assert second_player_stats.num_time_first_touch == 5
            assert second_player_stats.num_time_go_to_ball == 5
            for i in range(len(kickoffs)):
                kickoff = proto_game.game_stats.kickoff_stats[i]
                player = kickoff.touch.players[0]
                start_left = player.start_position.pos_x < 0
                assert player.start_left == start_left

        run_analysis_test_on_replay(test, get_raw_replays()["5_DIVERSE_KICKOFFS"])

    def test_all_kickoffs_2(self):
        def test(analysis: AnalysisManager):

            proto_game = analysis.get_protobuf_data()
            kickoffs = proto_game.game_stats.kickoffs
            assert (len(kickoffs) == 6)

            first_player = proto_game.players[0].stats
            kickoff_stats = first_player.kickoff_stats
            assert kickoff_stats.num_time_first_touch == 1
            assert kickoff_stats.num_time_go_to_ball == 1
            assert kickoff_stats.num_time_boost == 1
            assert kickoff_stats.num_time_cheat == 0
            assert kickoff_stats.num_time_defend == 1
            assert kickoff_stats.num_time_afk == 1
            assert kickoff_stats.total_kickoffs == 6
            assert 2 == (kickoff_stats.total_kickoffs -
                         (kickoff_stats.num_time_go_to_ball +
                          kickoff_stats.num_time_boost +
                          kickoff_stats.num_time_cheat +
                          kickoff_stats.num_time_defend +
                          kickoff_stats.num_time_afk))

            second_player_stats = proto_game.players[1].stats.kickoff_stats
            assert second_player_stats.num_time_first_touch == 5
            assert second_player_stats.num_time_go_to_ball == 6
            for i in range(len(kickoffs)):
                kickoff = proto_game.game_stats.kickoff_stats[i]
                player = kickoff.touch.players[0]
                start_left = player.start_position.pos_x < 0
                assert player.start_left == start_left

        run_analysis_test_on_replay(test, get_raw_replays()["6_DIVERSE_KICKOFFS"])
