from typing import Dict, List

from replay_analysis.analysis.stats.boost.boost import BoostStat
from replay_analysis.analysis.stats.possession.possession import PossessionStat
from replay_analysis.analysis.stats.stats import BaseStat
from replay_analysis.generated.api import game_pb2
from replay_analysis.generated.api.player_pb2 import Player
from replay_analysis.generated.api.stats.player_stats_pb2 import PlayerStats
from replay_analysis.generated.api.stats.team_stats_pb2 import TeamStats
from replay_analysis.generated.api.team_pb2 import Team
from replay_analysis.json_parser.game import Game


class StatsManager:
    def get_player_stats(self) -> List[BaseStat]:
        """These are stats that end up being assigned to a specific player"""
        return [BoostStat()]

    def get_team_stats(self) -> List[BaseStat]:
        """These are stats that end up being assigned to a specific team"""
        return [PossessionStat()]

    def get_general_stats(self) ->List[BaseStat]:
        """These are stats that end up being assigned to the game as a whole"""

    def get_stats(self, game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player],
                  data_frames):
        self.calculate_player_stats(game, proto_game, player_map, data_frames)
        self.calculate_team_stats(game, proto_game, proto_game.teams, player_map, data_frames)

    def calculate_team_stats(self, game: Game, proto_game: game_pb2.Game, teams: List[Team],
                             player_map: Dict[str, Player], data_frames):
        stats_proto: Dict[int, TeamStats] = {
            int(team.is_orange): team.stats
            for team in teams
        }
        for stat_function in self.get_team_stats():
            stat_function.calculate_team_stat(stats_proto, game, proto_game, player_map, data_frames)

    def calculate_player_stats(self, game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player],
                             data_frames):
        stats_proto: Dict[str, PlayerStats] = {
            key: player.stats
            for key, player in player_map.items()
        }
        for stat_function in self.get_player_stats():
            stat_function.calculate_player_stat(stats_proto, game, proto_game, player_map, data_frames)
