from carball.analysis.analysis_manager import AnalysisManager
from carball.tests.utils import run_analysis_test_on_replay, get_specific_replays


class Test_Team():

    def test_team_stat_creation(self, replay_cache):

        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()
            teams = proto_game.teams
            for team in teams:
                if team.is_orange:
                    continue
                assert (team.stats.center_of_mass.average_max_distance_from_center > 0)
                assert (team.stats.center_of_mass.average_distance_from_center > 0)
                assert (team.stats.center_of_mass.positional_tendencies.time_behind_ball > 0)

        run_analysis_test_on_replay(test, get_specific_replays()["PASSES"], cache=replay_cache)
