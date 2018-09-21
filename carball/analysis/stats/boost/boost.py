from typing import Dict

import numpy as np
import pandas as pd
from carball.analysis.constants.field_constants import FieldConstants

from carball.analysis.stats.utils.pandas_utils import sum_deltas_by_truthy_data
from ....analysis.stats.stats import BaseStat
from ....generated.api import game_pb2
from ....generated.api.player_pb2 import Player
from ....generated.api.stats.player_stats_pb2 import PlayerStats
from ....json_parser.game import Game


class BoostStat(BaseStat):

    field_constants = FieldConstants()

    def calculate_player_stat(self, player_stat_map: Dict[str, PlayerStats], game: Game, proto_game: game_pb2.Game,
                              player_map: Dict[str, Player], data_frame: pd.DataFrame):
        for player_key, stats in player_stat_map.items():
            proto_boost = stats.boost
            player_name = player_map[player_key].name
            player_data_frame = data_frame[player_name]
            proto_boost.boost_usage = self.get_player_boost_usage(player_data_frame)
            collection = self.get_player_boost_collection(player_data_frame)
            proto_boost.wasted_collection = self.get_player_boost_waste(proto_boost.boost_usage, collection)

            proto_boost.wasted_usage = self.get_player_boost_usage_max_speed(player_data_frame)
            if 'small' in collection and collection['small'] is not None:
                proto_boost.num_small_boosts = collection['small']
            if 'big' in collection and collection['big'] is not None:
                proto_boost.num_large_boosts = collection['big']

            proto_boost.time_full_boost = self.get_time_with_max_boost(data_frame, player_data_frame)
            proto_boost.time_low_boost = self.get_time_with_low_boost(data_frame, player_data_frame)
            proto_boost.time_no_boost = self.get_time_with_zero_boost(data_frame, player_data_frame)

            proto_boost.num_stolen_boosts = self.get_num_stolen_boosts(player_data_frame,
                                                                       player_map[player_key].is_orange)

    @staticmethod
    def get_player_boost_usage(player_dataframe: pd.DataFrame) -> np.float64:
        _diff = -player_dataframe.boost.diff()
        boost_usage = _diff[_diff > 0].sum() / 255 * 100
        return boost_usage

    @classmethod
    def get_num_stolen_boosts(cls, player_dataframe: pd.DataFrame, is_orange):
        big_pads_collected = player_dataframe[player_dataframe.boost_collect == True]
        if is_orange == 1:
            boost_collected_in_opposing_third = big_pads_collected[cls.field_constants.get_third_0(big_pads_collected)]
        else:
            boost_collected_in_opposing_third = big_pads_collected[cls.field_constants.get_third_2(big_pads_collected)]

        return len(boost_collected_in_opposing_third.index)

    @staticmethod
    def get_player_boost_usage_max_speed(player_dataframe: pd.DataFrame) -> np.float64:
        _diff = -player_dataframe.boost.diff()

        speed: pd.Series = (player_dataframe.vel_x ** 2 +
                            player_dataframe.vel_y ** 2 +
                            player_dataframe.vel_z ** 2) ** 0.5

        _diff = _diff.rename('boost')
        speed = speed.rename('speed')

        combined = pd.concat([_diff, speed], axis=1)

        wasted_boost = combined[(combined.speed > 22000) & (combined.boost > 0) & (combined.boost < 10)]
        boost_usage = wasted_boost.boost.sum() / 255 * 100
        return boost_usage

    @staticmethod
    def get_time_with_max_boost(data_frame: pd.DataFrame, player_dataframe: pd.DataFrame) -> np.float64:
        return sum_deltas_by_truthy_data(data_frame, player_dataframe.boost > 252.45)  # 100% visible boost

    @staticmethod
    def get_time_with_low_boost(data_frame: pd.DataFrame, player_dataframe: pd.DataFrame) -> np.float64: # less than 25
        return sum_deltas_by_truthy_data(data_frame, player_dataframe.boost < 63.75)  # 25 / 100 * 255

    @staticmethod
    def get_time_with_zero_boost(data_frame: pd.DataFrame, player_dataframe: pd.DataFrame) -> np.float64: # at 0 boost
        return sum_deltas_by_truthy_data(data_frame, player_dataframe.boost == 0)

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
