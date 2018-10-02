from typing import Dict

import pandas as pd

from carball.analysis.constants.basic_math import get_player_ball_displacements, get_distance_from_displacements, \
    get_position_displacements
from ....analysis.stats.utils.pandas_utils import sum_deltas_by_player_name
from ....analysis.stats.stats import BaseStat
from ....generated.api import game_pb2
from ....generated.api.player_pb2 import Player
from ....generated.api.stats.player_stats_pb2 import PlayerStats
from ....json_parser.game import Game


class BallDistanceStat(BaseStat):

    def calculate_player_stat(self, player_stat_map: Dict[str, PlayerStats], game: Game, proto_game: game_pb2.Game,
                              player_map: Dict[str, Player], data_frame: pd.DataFrame):

        player_distances_data_frame, player_distance_times, player_distance_with_delta, \
             = self.calculate_player_distance_to_location(player_map, data_frame,
                                                          data_frame['ball'])

        for player_id in player_stat_map.keys():
            close_frames = player_distances_data_frame[player_id] < 500
            time_close_to_ball = player_distance_with_delta[close_frames]['delta'].sum()
            distance_stats = player_stat_map[player_id].distance

            distance_stats.time_close_to_ball = time_close_to_ball

            try:
                distance_stats.time_closest_to_ball = player_distance_times['closest_player'][player_id]
                distance_stats.time_furthest_from_ball = player_distance_times['furthest_player'][player_id]
            except (AttributeError, KeyError):
                distance_stats.time_closest_to_ball = 0
                distance_stats.time_furthest_from_ball = 0

    @staticmethod
    def calculate_player_distance_to_location(player_map: Dict[str, Player], data_frame: pd.DataFrame,
                                              location: pd.DataFrame) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
        """
        Calculates the player distance to a particular location
        also grabbing the closest and furthest player to those locations.
        :param player_map:
        :param data_frame:
        :param location:
        :return:
        """
        player_displacements = {player_id: get_position_displacements(data_frame[player_map[player_id].name],
                                                                      location)
                                for player_id in player_map.keys()}

        player_distances = {player_id: get_distance_from_displacements(player_data_frame).rename(player_id)
                            for player_id, player_data_frame in player_displacements.items()}

        player_distances_data_frame = pd.concat(player_distances, axis=1)
        closest_players = player_distances_data_frame.idxmin(axis=1).rename('closest_player')
        furthest_players = player_distances_data_frame.idxmax(axis=1).rename('furthest_player')
        player_distance_with_delta = pd.concat([player_distances_data_frame, data_frame['game', 'delta'].rename('delta')], axis=1)

        player_ball_distance_times = pd.concat([
            sum_deltas_by_player_name(data_frame, players_data_frame)
            for players_data_frame in [closest_players, furthest_players]
        ], axis=1)

        player_ball_distance_times.fillna(value=0, inplace=True)
        return player_distances_data_frame, player_ball_distance_times, player_distance_with_delta
