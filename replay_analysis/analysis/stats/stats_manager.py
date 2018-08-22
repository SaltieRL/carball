from typing import Dict, Callable, List

from replay_analysis.generated.api import game_pb2
from replay_analysis.generated.api.player_pb2 import Player
from replay_analysis.generated.api.team_pb2 import Team
from replay_analysis.json_parser.game import Game


class StatsManager:
    def get_player_stats(self) -> Dict[str, Callable]:
        """These are stats that end up being assigned to a specific player"""


    def get_team_stats(self) -> Dict[str, Callable]:
        """These are stats that end up being assigned to a specific player"""


    def get_general_stats(self) ->Dict[str, Callable]:
        """These are stats that end up being assigned to the game as a whole"""


    def get_stats(self, game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player],
                  data_frames, kickoff_frames):

    def calculate_team_stats(self, game: Game, teams: List[Team], player_map: Dict[str, Player],
                             data_frames, kickoff_frames):
        stats_proto = [team.stats for team in teams]
        for field_name, stat_function in self.get_team_stats():
            stats = stat_function(game, player_map, data_frames)
