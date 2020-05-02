import logging
from typing import Dict

import numpy as np
import pandas as pd
from carball.analysis.constants.field_constants import FieldConstants

from carball.analysis.stats.utils.pandas_utils import sum_deltas_by_truthy_data
from ....analysis.stats.stats import BaseStat
from ....generated.api import game_pb2
from ....generated.api.player_pb2 import Player
from ....generated.api.stats.player_stats_pb2 import PlayerStats
from ....json_parser.actor.boost import BOOST_PER_SECOND
from ....json_parser.game import Game

logger = logging.getLogger(__name__)


class BoostStat(BaseStat):
    field_constants = FieldConstants()

    def calculate_player_stat(self, player_stat_map: Dict[str, PlayerStats], game: Game, proto_game: game_pb2.Game,
                              player_map: Dict[str, Player], data_frame: pd.DataFrame):
        for player_key, stats in player_stat_map.items():

            proto_boost = stats.boost
            player_name = player_map[player_key].name
            player_data_frame = data_frame[player_name].copy()
            player_data_frame.loc[:, 'delta'] = data_frame['game'].delta
            proto_boost.boost_usage = self.get_player_boost_usage(player_data_frame)

            proto_boost.wasted_usage = self.get_player_boost_usage_max_speed(player_data_frame)

            proto_boost.time_full_boost = self.get_time_with_max_boost(data_frame, player_data_frame)
            proto_boost.time_low_boost = self.get_time_with_low_boost(data_frame, player_data_frame)
            proto_boost.time_no_boost = self.get_time_with_zero_boost(data_frame, player_data_frame)
            proto_boost.average_boost_level = self.get_average_boost_level(player_data_frame)

            if 'boost_collect' not in player_data_frame:
                logger.warning('%s did not collect any boost', player_key)
            else:
                gains_index = player_data_frame['boost'].diff().clip(0)
                gains_index = gains_index.loc[gains_index > 0].index.to_numpy()
                collect_frames = player_data_frame.loc[player_data_frame.index[player_data_frame['boost_collect'] > 34]]
                # Have to loop to fuzzy match
                wasted_big = 0
                for index in collect_frames.index.to_numpy():
                    idx = gains_index[(np.abs(gains_index - index).argmin())]
                    int_idx = player_data_frame.index.get_loc(idx)
                    wasted_big += player_data_frame['boost'].iloc[int_idx - 1] / 256 * 100

                collect_frames = player_data_frame.loc[player_data_frame.index[player_data_frame['boost_collect'] <= 34]]
                prior_vals = np.empty([0])
                for index in collect_frames.index.to_numpy():
                    idx = gains_index[(np.abs(gains_index - index).argmin())]
                    int_idx = player_data_frame.index.get_loc(idx)
                    val = player_data_frame['boost'].iloc[int_idx-1]
                    prior_vals = np.append(prior_vals, val)
                deltas = ((prior_vals + 30.6) - 255)
                wasted_small = deltas[deltas > 0].sum() / 256 * 100

                collection = self.get_player_boost_collection(player_data_frame)
                proto_boost.wasted_collection = wasted_big + wasted_small
                proto_boost.wasted_big = wasted_big
                proto_boost.wasted_small = wasted_small

                if 'small' in collection and collection['small'] is not None:
                    proto_boost.num_small_boosts = collection['small']
                if 'big' in collection and collection['big'] is not None:
                    proto_boost.num_large_boosts = collection['big']

                proto_boost.num_stolen_boosts = self.get_num_stolen_boosts(player_data_frame,
                                                                           player_map[player_key].is_orange)

    @staticmethod
    def get_player_boost_usage(player_dataframe: pd.DataFrame) -> np.float64:
        return (BOOST_PER_SECOND * (player_dataframe.delta * player_dataframe.boost_active)).sum() / 255 * 100
        # _diff = -player_dataframe.boost.diff()
        # boost_usage = _diff[_diff > 0].sum() / 255 * 100
        # return boost_usage

    @staticmethod
    def get_average_boost_level(player_dataframe: pd.DataFrame) -> np.float64:
        return player_dataframe.boost.mean(skipna=True) / 255 * 100

    @classmethod
    def get_num_stolen_boosts(cls, player_dataframe: pd.DataFrame, is_orange):
        big = cls.field_constants.get_big_pads()
        # Get big pads below or above 0 depending on team
        # The index of y position is 1. The index of the label is 2.
        if is_orange:
            opponent_pad_labels = big[big[:, 1] < 0][:, 2] #big[where[y] is < 0][labels]
        else:
            opponent_pad_labels = big[big[:, 1] > 0][:, 2] #big[where[y] is > 0][labels]
        # Count all the places where isin = True by summing
        stolen = player_dataframe.boost_collect.isin(opponent_pad_labels).sum()
        return stolen

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
    def get_time_with_low_boost(data_frame: pd.DataFrame, player_dataframe: pd.DataFrame) -> np.float64:  # less than 25
        return sum_deltas_by_truthy_data(data_frame, player_dataframe.boost < 63.75)  # 25 / 100 * 255

    @staticmethod
    def get_time_with_zero_boost(data_frame: pd.DataFrame, player_dataframe: pd.DataFrame) -> np.float64:  # at 0 boost
        return sum_deltas_by_truthy_data(data_frame, player_dataframe.boost == 0)

    @staticmethod
    def get_player_boost_collection(player_dataframe: pd.DataFrame) -> Dict[str, int]:
        try:
            big_counts = (player_dataframe['boost_collect'] > 34).sum()
            small_counts = (player_dataframe['boost_collect'] <= 34).sum()
            ret = {}
            if big_counts > 0:
                ret['big'] = big_counts
            if small_counts > 0:
                ret['small'] = small_counts
        except (AttributeError, KeyError):
            return {}
        return ret
