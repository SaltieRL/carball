from typing import TYPE_CHECKING, Dict

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from ...saltie_game.saltie_game import SaltieGame


class BoostStat:
    def __init__(self,
                 usage: Dict[str, np.float64],
                 collection: Dict[str, Dict[str, int]],
                 waste: Dict[str, np.float64]):
        self.usage = usage
        self.collection = collection
        self.waste = waste

    @classmethod
    def get_boost(cls, saltie_game: 'SaltieGame') -> 'BoostStat':
        goal_frames = saltie_game.data_frame.game.goal_number.notnull()

        usage: Dict[str, np.float64] = {
            player.name: cls.get_player_boost_usage(saltie_game.data_frame[player.name][goal_frames])
            for team in saltie_game.api_game.teams for player in team.players
        }

        collection: Dict[str, Dict[str, int]] = {
            player.name: cls.get_player_boost_collection(saltie_game.data_frame[player.name][goal_frames])
            for team in saltie_game.api_game.teams for player in team.players
        }

        waste: Dict[str, np.float64] = {
            player.name: cls.get_player_boost_waste(usage[player.name], collection[player.name])
            for team in saltie_game.api_game.teams for player in team.players
        }
        return cls(usage=usage, collection=collection, waste=waste)

    @staticmethod
    def get_player_boost_usage(player_dataframe: pd.DataFrame) -> np.float64:
        _diff = -player_dataframe.boost.diff()
        boost_usage = _diff[_diff > 0].sum() / 255 * 100
        return boost_usage

    @staticmethod
    def get_player_boost_collection(player_dataframe: pd.DataFrame) -> Dict[str, int]:
        value_counts = player_dataframe.boost_collect.value_counts()
        return {
            'big': value_counts[True],
            'small': value_counts[False]
        }

    @staticmethod
    def get_player_boost_waste(usage: np.float64, collection: Dict[str, int]) -> float:
        total_collected = collection['big'] * 100 + collection['small'] * 12
        return total_collected - usage
