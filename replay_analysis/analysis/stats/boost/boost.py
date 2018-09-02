from typing import Dict

import numpy as np
import pandas as pd

from ....analysis.stats.stats import BaseStat
from ....generated.api import game_pb2
from ....generated.api.player_pb2 import Player
from ....generated.api.stats.player_stats_pb2 import PlayerStats
from ....json_parser.game import Game


class BoostStat(BaseStat):

    def calculate_player_stat(self, player_stat_map: Dict[str, PlayerStats], game: Game, proto_game: game_pb2.Game,
                              player_map: Dict[str, Player], data_frame: pd.DataFrame):
        for player_key, stats in player_stat_map.items():
            proto_boost = stats.boost
            player_name = player_map[player_key].name
            proto_boost.usage = self.get_player_boost_usage(data_frame[player_name])
            collection = self.get_player_boost_collection(data_frame[player_name])
            proto_boost.wasted_collection = self.get_player_boost_waste(proto_boost.usage, collection)
            if 'small' in collection and collection['small'] is not None:
                proto_boost.num_small_boosts = collection['small']
            if 'big' in collection and collection['big'] is not None:
                proto_boost.num_large_boosts = collection['big']

    @staticmethod
    def get_player_boost_usage(player_dataframe: pd.DataFrame) -> np.float64:
        _diff = -player_dataframe.boost.diff()
        boost_usage = _diff[_diff > 0].sum() / 255 * 100
        return boost_usage

    @staticmethod
    def get_player_boost_usage_max_speed(player_dataframe: pd.DataFrame) -> np.float64:
        """TODO: do this"""
        _diff = -player_dataframe.boost.diff()
        boost_usage = _diff[_diff > 0].sum() / 255 * 100
        return boost_usage

    @staticmethod
    def get_player_boost_collection(player_dataframe: pd.DataFrame) -> Dict[str, int]:
        value_counts = player_dataframe.boost_collect.value_counts()
        try:
            return {
                'big': int(value_counts[True]),
                'small': int(value_counts[False])
            }
        except KeyError:
            return {}

    @staticmethod
    def get_player_boost_waste(usage: np.float64, collection: Dict[str, int]) -> float:
        try:
            total_collected = collection['big'] * 100 + collection['small'] * 12
            return total_collected - usage
        except KeyError:
            return 0
