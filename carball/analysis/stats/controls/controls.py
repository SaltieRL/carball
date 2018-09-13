from typing import Dict

import pandas as pd

from ....analysis.stats.stats import BaseStat
from ....generated.api import game_pb2
from ....generated.api.player_pb2 import Player
from ....generated.api.stats.player_stats_pb2 import PlayerStats
from ....json_parser.game import Game

class ControlsStat(BaseStat):

    def calculate_player_stat(self, player_stat_map: Dict[str, PlayerStats], game: Game, proto_game: game_pb2.Game,
                              player_map: Dict[str, Player], data_frame: pd.DataFrame):
        for player_key, stats in player_map.items():
            player_name = player_map[player_key].name

            steering_percentage = self.get_analogue_percentage("steer", data_frame, player_name)
            throttle_percentage = self.get_analogue_percentage("throttle", data_frame, player_name)
            is_keyboard = bool((steering_percentage == 0) and (throttle_percentage == 0))

            controller_stats = player_stat_map[player_key].controller
            controller_stats.is_keyboard = is_keyboard
            controller_stats.analogue_steering_input_percent = throttle_percentage
            controller_stats.analogue_throttle_input_percent = steering_percentage

    def get_analogue_percentage(self, column: str, data_frame: pd.DataFrame, player_name: str):
        total_frames = len(data_frame[player_name][column])
        count = (data_frame[player_name][column] == 0).sum() + (data_frame[player_name][column] == 128).sum()  + (data_frame[player_name][column] == 255).sum() + data_frame[player_name][column].isna().sum()
        return 100 - ((count * 100) / total_frames)
    