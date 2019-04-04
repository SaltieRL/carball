import unittest
from carball.analysis.analysis_manager import AnalysisManager
from carball.tests.utils import run_analysis_test_on_replay, get_raw_replays


class LeaderTest(unittest.TestCase):

    def test_0_play_station_only_party(self):
        def test(analysis: AnalysisManager):
            game = analysis.game
            ps_party_leader = "['jamesvento98', [134, 204, 174, 206, 14, 206, 44, 0, 128, 0, 0, 0, 0, 0, 0, 0, 236, 247, 155, 189, 79, 103, 54, 42]]"
            ps_team_member_01 = "['hronaldMCdonald', [38, 76, 174, 206, 14, 206, 44, 0, 128, 0, 0, 0, 0, 0, 0, 0, 74, 205, 11, 172, 194, 210, 7, 2]]"
            ps_team_member_03 = "['DaFunnyWhiteGuy', [198, 204, 174, 206, 14, 206, 44, 0, 128, 0, 0, 0, 0, 0, 0, 0, 140, 122, 205, 218, 14, 248, 148, 34]]"
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
            party_01_member_02 = "1011111101011101001001001101110111011010001011100111001000010100000110010110001000010100001100100111011100010100000000000000100001011101010100101011000010111101101010110111100010101001000111110000100110010100001100011001000000110100000000000000000000000000"

            party_02_leader = "['DON_FULL_S3ND_1T', [70, 44, 174, 206, 14, 206, 44, 0, 128, 0, 0, 0, 0, 0, 0, 0, 36, 178, 0, 36, 190, 50, 177, 74]]"
            party_02_member_01 = party_02_leader
            party_02_member_02 = "['freakyfitnig100', [70, 76, 174, 206, 14, 206, 44, 0, 128, 0, 0, 0, 0, 0, 0, 0, 169, 39, 75, 227, 93, 88, 117, 152]]"

            self.assertIn(party_01_leader, game.parties.keys())
            self.assertIn(party_01_member_01, game.parties[party_01_leader])
            self.assertIn(party_01_member_02, game.parties[party_01_leader])

            self.assertIn(party_02_leader, game.parties.keys())
            self.assertIn(party_02_member_01, game.parties[party_02_leader])
            self.assertIn(party_02_member_02, game.parties[party_02_leader])

        run_analysis_test_on_replay(test, get_raw_replays()["PARTY_LEADER_SYSTEM_ID_0_ERROR"])


if __name__ == '__main__':
    unittest.main()
