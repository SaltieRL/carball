import logging
import time
from typing import Dict, List

import pandas as pd

from ...analysis.stats.stats_list import StatsList
from ...generated.api import game_pb2
from ...generated.api.player_pb2 import Player
from ...generated.api.stats.player_stats_pb2 import PlayerStats
from ...generated.api.stats.team_stats_pb2 import TeamStats
from ...generated.api.team_pb2 import Team
from ...json_parser.game import Game


logger = logging.getLogger(__name__)


def start_time():
    return time.time()

def end_time(start):
    return (time.time() - start) * 1000


class StatsManager:

    def get_stats(self, game: Game, proto_game: game_pb2.Game,
                  player_map: Dict[str, Player], data_frame: pd.DataFrame):
        """
        Calculates all advanced stats.
        The stats are always calculated in this order:
            Player, Team, Game, Hit
        """
        self.calculate_player_stats(game, proto_game, player_map, data_frame)
        self.calculate_team_stats(game, proto_game, proto_game.teams, player_map, data_frame)
        self.calculate_game_stats(game, proto_game, player_map, data_frame)
        self.calculate_hit_stats(game, proto_game, player_map, data_frame)

    @staticmethod
    def calculate_player_stats(game: Game, proto_game: game_pb2.Game,
                               player_map: Dict[str, Player], data_frame: pd.DataFrame):
        stats_proto: Dict[str, PlayerStats] = {
            key: player.stats
            for key, player in player_map.items()
        }
        for stat_function in StatsList.get_player_stats():
            time = start_time()
            logger.debug("Building player stat: %s", type(stat_function).__name__)
            stat_function.calculate_player_stat(stats_proto, game, proto_game, player_map, data_frame)
            logger.debug("Built in [%d] milliseconds", end_time(time))

    @staticmethod
    def calculate_team_stats(game: Game, proto_game: game_pb2.Game, teams: List[Team],
                             player_map: Dict[str, Player], data_frame: pd.DataFrame):
        stats_proto: Dict[int, TeamStats] = {
            int(team.is_orange): team.stats
            for team in teams
        }
        for stat_function in StatsList.get_team_stats():
            time = start_time()
            logger.debug("Building team stat: %s", type(stat_function).__name__)
            stat_function.calculate_team_stat(stats_proto, game, proto_game, player_map, data_frame)
            logger.debug("Built in [%d] milliseconds", end_time(time))

    @staticmethod
    def calculate_game_stats(game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player],
                             data_frame: pd.DataFrame):
        for stat_function in StatsList.get_general_stats():
            time = start_time()
            logger.debug("Building game stat: %s", type(stat_function).__name__)
            stat_function.calculate_stat(proto_game.game_stats, game, proto_game, player_map, data_frame)
            logger.debug("Built in [%d] milliseconds", end_time(time))

    @staticmethod
    def calculate_hit_stats(game: Game, proto_game: game_pb2.Game,
                            player_map: Dict[str, Player], data_frame: pd.DataFrame):
        hit_stats = StatsList.get_hit_stats()
        for hit_stat in hit_stats:
            logger.debug("Building hit stat: %s", type(hit_stat).__name__)
            hit_stat.initialize_hit_stat(game, player_map, data_frame)
        hits = proto_game.game_stats.hits
        for hit_index in range(len(hits) - 1):
            current_hit = hits[hit_index]
            if current_hit.HasField("next_hit_frame_number"):
                next_hit = hits[hit_index + 1]
                for hit_stat in hit_stats:
                    hit_stat.calculate_next_hit_stat(game, proto_game, current_hit, next_hit, player_map, hit_index)
