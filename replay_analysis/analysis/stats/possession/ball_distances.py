from typing import Dict

import pandas as pd

from ....analysis.hit_detection.base_hit import get_distance_from_displacements, get_player_ball_displacements
from ....analysis.stats.stats import BaseStat
from ....generated.api import game_pb2
from ....generated.api.player_pb2 import Player
from ....generated.api.stats.player_stats_pb2 import PlayerStats
from ....json_parser.game import Game


class BallDistanceStat(BaseStat):

    def calculate_player_stat(self, player_stat_map: Dict[str, PlayerStats], game: Game, proto_game: game_pb2.Game,
                              player_map: Dict[str, Player], data_frame: pd.DataFrame):
        player_names = [player_map[player_id].name for player_id in player_stat_map.keys()]
        player_displacements = {player_name: get_player_ball_displacements(data_frame, player_name)
                                for player_name in player_names}

        player_distances = {player_name: get_distance_from_displacements(player_data_frame).rename(player_name)
                             for player_name, player_data_frame in player_displacements.items()}

        player_distances_data_frame = pd.concat(player_distances, axis=1)
        closest_players = player_distances_data_frame.idxmin(axis=1)
        furthest_players = player_distances_data_frame.idxmax(axis=1)
        self.return_time_by_player(data_frame, closest_players)
        for player_id, stat in player_stat_map.items():
            print(player_distances)



    def return_time_by_player(self, data_frame, player_frame):
        combined_data = pd.concat([player_frame, data_frame['game', 'delta']])
        combined_data.groupby('hit_team_no').sum()
