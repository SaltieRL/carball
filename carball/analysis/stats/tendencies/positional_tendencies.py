from typing import Callable, Dict

import pandas as pd

from ....analysis.constants.field_constants import FieldConstants
from ....analysis.stats.stats import BaseStat
from ....generated.api import game_pb2
from ....generated.api.player_pb2 import Player
from ....generated.api.stats import stats_pb2
from ....generated.api.stats.player_stats_pb2 import PlayerStats
from ....json_parser.game import Game


class PositionalTendencies(BaseStat):
    field_constants = FieldConstants()

    def __init__(self):
        super().__init__()
        self.field_constants = FieldConstants()
        self.map_player_attributes_to_predicates = {
            "height_0": self.field_constants.get_height_0,
            "height_1": self.field_constants.get_height_1,
            "height_2": self.field_constants.get_height_2,
            "half_0": self.field_constants.get_half_0,
            "half_1": self.field_constants.get_half_1,
            "third_0": self.field_constants.get_third_0,
            "third_1": self.field_constants.get_third_1,
            "third_2": self.field_constants.get_third_2,
            "ball_0": self.field_constants.get_ball_0,
            "ball_1": self.field_constants.get_ball_1,
            "wall": self.field_constants.get_wall_time,
            "corner": self.field_constants.get_corner_time
        }

        self.map_ball_attributes_to_predicates = {
            "height_0": self.field_constants.get_height_0_ball,
            "height_1": self.field_constants.get_height_1,
            "height_2": self.field_constants.get_height_2,
            "half_0": self.field_constants.get_half_0,
            "half_1": self.field_constants.get_half_1,
            "third_0": self.field_constants.get_third_0,
            "third_1": self.field_constants.get_third_1,
            "third_2": self.field_constants.get_third_2,
            "ball_0": self.field_constants.get_ball_0,
            "ball_1": self.field_constants.get_ball_1,
            "wall": self.field_constants.get_wall_time,
            "corner": self.field_constants.get_corner_time
        }

    def calculate_player_stat(self, player_stat_map: Dict[str, PlayerStats], game: Game, proto_game: game_pb2.Game,
                              player_map: Dict[str, Player], data_frame: pd.DataFrame):
        for id, player in player_map.items():
            self.get_player_tendencies(player, data_frame)

    def calculate_stat(self, proto_stat, game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player],
                       data_frame: pd.DataFrame):
        ball_data_frame = data_frame['ball']

        self.get_tendencies(data_frame, ball_data_frame, ball_data_frame, False,
                            proto_stat.ball_stats.positional_tendencies, self.map_ball_attributes_to_predicates)

    def get_player_tendencies(self, player: Player, data_frame: pd.DataFrame):
        self.get_tendencies(data_frame, data_frame[player.name], data_frame['ball'],
                            player.is_orange, player.stats.positional_tendencies,
                            self.map_player_attributes_to_predicates)

    def get_tendencies(self, data_frame: pd.DataFrame, player_data_frame: pd.DataFrame,
                       ball_data_frame: pd.DataFrame, is_orange: bool,
                       positional_tendencies: stats_pb2.PositionalTendencies,
                       predicate_map: Dict[str, Callable]):
        """
        Calculates the tendencies for all of the stats
        :param data_frame: The normal data frame
        :param player_data_frame: The frame for the positions of the player
        :param ball_data_frame: The frame for the positions of the ball
        :param is_orange: If we need to flip the field for defense/offense
        :param positional_tendencies: The proto field where everything is set
        :param predicate_map: The map of checks to call
        """
        player_ball_dataframes: Dict[str, pd.DataFrame] = {
            "player_data_frame": player_data_frame,
            "ball_data_frame": ball_data_frame,
        }
        if is_orange:
            player_ball_dataframes = self.get_flipped_dataframes(player_ball_dataframes)

        init_params = {
            attr: self.get_duration_from_predicate(predicate, player_ball_dataframes, data_frame)
            for attr, predicate in predicate_map.items()
        }
        self.set_tendency_proto(positional_tendencies, **init_params)

    @staticmethod
    def get_duration_from_predicate(predicate: Callable,
                                    player_ball_dataframes: Dict[str, pd.DataFrame], data_frame: pd.DataFrame):
        boolean_index = predicate(**player_ball_dataframes)
        deltas = data_frame.game.delta
        return deltas[boolean_index].sum()

    def get_flipped_dataframes(self, data_frames: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        new_dataframes = {
            _k: _v.copy() for _k, _v in data_frames.items()
        }

        for data_frame in new_dataframes.values():
            data_frame.pos_y *= -1
            data_frame.rot_y += 65535 / 2
            data_frame.rot_y %= 65536

        return new_dataframes

    @staticmethod
    def set_tendency_proto(proto: stats_pb2.PositionalTendencies, height_0: float, height_1: float, height_2: float,
                           half_0: float, half_1: float,
                           third_0: float, third_1: float, third_2: float,
                           ball_0: float, ball_1: float,
                           wall: float, corner: float
                           ):
        """
        :param proto: What object everything is getting set on
        :param height_0: Time spent on ground
        :param height_1: Time spent low in air
        :param height_2: Time spent high in air
        :param half_0: Time spent in defending half
        :param half_1: Time spent in attacking half
        :param third_0: Time spent in defending third
        :param third_1: Time spent in middle third
        :param third_2: Time spent in attacking third
        :param ball_0: Time spent behind ball
        :param ball_1: Time spent ahead of ball
        :param wall: Time spent near the wall
        :param corner: Time spent near the corner
        """
        proto.time_on_ground = height_0
        proto.time_low_in_air = height_1
        proto.time_high_in_air = height_2
        proto.time_in_defending_half = half_0
        proto.time_in_attacking_half = half_1
        proto.time_in_defending_third = third_0
        proto.time_in_neutral_third = third_1
        proto.time_in_attacking_third = third_2
        proto.time_behind_ball = ball_0
        proto.time_in_front_ball = ball_1
        proto.time_near_wall = wall
        proto.time_in_corner = corner
