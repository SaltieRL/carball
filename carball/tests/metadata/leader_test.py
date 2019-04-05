import unittest
from carball.analysis.analysis_manager import AnalysisManager
from carball.tests.utils import run_analysis_test_on_replay, get_raw_replays


class LeaderTest(unittest.TestCase):

    def test_0_play_station_only_party(self):
        def test(analysis: AnalysisManager):
            game = analysis.game
            ps_party_leader = "6083491126912347959"
            ps_team_member_01 = "4674819165248336722"
            ps_team_member_03 = "4911491436059516465"
            ps_team_member_02 = ps_party_leader

            self.assertIn(ps_party_leader, game.parties.keys())
            self.assertIn(ps_team_member_01, game.parties[ps_party_leader])
            self.assertIn(ps_team_member_02, game.parties[ps_party_leader])
            self.assertIn(ps_team_member_03, game.parties[ps_party_leader])

        run_analysis_test_on_replay(test, get_raw_replays()["PLAY_STATION_ONLY_PARTY"])

    def test_1_party_leader_system_id_0(self):
        def test(analysis: AnalysisManager):
            game = analysis.game

            party_01_leader = "76561198084378722"
            party_01_member_01 = party_01_leader
            party_01_member_02 = "2904386747031141117"

            party_02_leader = "5948494783184915748"
            party_02_member_01 = party_02_leader
            party_02_member_02 = "1850445886414578837"

            self.assertIn(party_01_leader, game.parties.keys())
            self.assertIn(party_01_member_01, game.parties[party_01_leader])
            self.assertIn(party_01_member_02, game.parties[party_01_leader])

            self.assertIn(party_02_leader, game.parties.keys())
            self.assertIn(party_02_member_01, game.parties[party_02_leader])
            self.assertIn(party_02_member_02, game.parties[party_02_leader])

        run_analysis_test_on_replay(test, get_raw_replays()["PARTY_LEADER_SYSTEM_ID_0_ERROR"])

    def test_2_xbox_party(self):
        def test(analysis: AnalysisManager):
            game = analysis.game

            party_01_leader = "76561198084378722"
            party_01_member_01 = party_01_leader
            party_01_member_02 = "2904386747031141117"

            party_02_leader = "2535465181947426"
            party_02_member_01 = party_02_leader
            party_02_member_02 = "2535416417939826"

            self.assertIn(party_01_leader, game.parties.keys())
            self.assertIn(party_01_member_01, game.parties[party_01_leader])
            self.assertIn(party_01_member_02, game.parties[party_01_leader])

            self.assertIn(party_02_leader, game.parties.keys())
            self.assertIn(party_02_member_01, game.parties[party_02_leader])
            self.assertIn(party_02_member_02, game.parties[party_02_leader])

        run_analysis_test_on_replay(test, get_raw_replays()["XBOX_PARTY"])


if __name__ == '__main__':
    unittest.main()
