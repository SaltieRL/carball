from typing import Dict, List

from replay_analysis.analysis.stats.stats_list import StatsList
from replay_analysis.generated.api import game_pb2
from replay_analysis.generated.api.player_pb2 import Player
from replay_analysis.generated.api.stats.player_stats_pb2 import PlayerStats
from replay_analysis.generated.api.stats.team_stats_pb2 import TeamStats
from replay_analysis.generated.api.team_pb2 import Team
from replay_analysis.json_parser.game import Game


class StatsManager:

    def get_stats(self, game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player],
                  data_frames):
        self.calculate_player_stats(game, proto_game, player_map, data_frames)
        self.calculate_team_stats(game, proto_game, proto_game.teams, player_map, data_frames)
        self.calculate_game_stats(game, proto_game, player_map, data_frames)
        self.calculate_hit_stats(game, proto_game, player_map, data_frames)

    def calculate_game_stats(self, game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player],
                             data_frames):
        for stat_funciton in StatsList.get_general_stats():
            stat_funciton.calculate_stat(proto_game.game_stats, game, proto_game, player_map, data_frames)

    def calculate_team_stats(self, game: Game, proto_game: game_pb2.Game, teams: List[Team],
                             player_map: Dict[str, Player], data_frames):
        stats_proto: Dict[int, TeamStats] = {
            int(team.is_orange): team.stats
            for team in teams
        }
        for stat_function in StatsList.get_team_stats():
            stat_function.calculate_team_stat(stats_proto, game, proto_game, player_map, data_frames)

    def calculate_player_stats(self, game: Game, proto_game: game_pb2.Game,
                               player_map: Dict[str, Player], data_frames):
        stats_proto: Dict[str, PlayerStats] = {
            key: player.stats
            for key, player in player_map.items()
        }
        for stat_function in StatsList.get_player_stats():
            stat_function.calculate_player_stat(stats_proto, game, proto_game, player_map, data_frames)

    def calculate_hit_stats(self, game: Game, proto_game: game_pb2.Game,
                            player_map: Dict[str, Player], data_frames):
        hit_stats = StatsList.get_hit_stats()
        for hit_stat in hit_stats:
            hit_stat.initialize_hit_stat(game, player_map, data_frames)
        hits = proto_game.game_stats.hits
        for hit_index in range(len(hits) - 1):
            current_hit = hits[hit_index]
            if current_hit.HasField("next_hit_frame_number"):
                next_hit = hits[hit_index + 1]
                for hit_stat in hit_stats:
                    hit_stat.calculate_next_hit_stat(game, proto_game, current_hit, next_hit, player_map)
