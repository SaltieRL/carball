from typing import TYPE_CHECKING, Callable, Dict

import pandas as pd

from .predicates.position import *

if TYPE_CHECKING:
    from replay_analysis.analysis import SaltieGame
    from replay_analysis.analysis.saltie_game.metadata.ApiPlayer import ApiPlayer


class PositionalTendencies:

    def __init__(self,
                 height_0: float, height_1: float, height_2: float,
                 half_0: float, half_1: float,
                 third_0: float, third_1: float, third_2: float,
                 ball_0: float, ball_1: float,
                 ):
        """
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
        """
        self.height_0 = height_0
        self.height_1 = height_1
        self.height_2 = height_2
        self.half_0 = half_0
        self.half_1 = half_1
        self.third_0 = third_0
        self.third_1 = third_1
        self.third_2 = third_2
        self.ball_0 = ball_0
        self.ball_1 = ball_1

    def __repr__(self):
        return str({_k: "{:.2f}".format(_v) for _k, _v in self.__dict__.items()})

    @classmethod
    def get_player_tendencies_for_game(cls, saltie_game: 'SaltieGame'):
        return {
            player.name: cls.get_player_tendencies(player, saltie_game)
            for team in saltie_game.api_game.teams for player in team.players
        }

    @classmethod
    def get_player_tendencies(cls, player: 'ApiPlayer', saltie_game: 'SaltieGame') -> 'PositionalTendencies':
        player_dataframe = saltie_game.data_frame[player.name]
        ball_dataframe = saltie_game.data_frame['ball']
        dataframes: Dict[str, pd.DataFrame] = {
            "player_dataframe": player_dataframe,
            "ball_dataframe": ball_dataframe
        }
        if player.is_orange:
            dataframes = cls.get_flipped_dataframes(dataframes)

        map_attributes_to_predicates = {
            "height_0": get_height_0,
            "height_1": get_height_1,
            "height_2": get_height_2,
            "half_0": get_half_0,
            "half_1": get_half_1,
            "third_0": get_third_0,
            "third_1": get_third_1,
            "third_2": get_third_2,
            "ball_0": get_ball_0,
            "ball_1": get_ball_1
        }

        init_params = {
            attr: cls.get_duration_from_predicate(predicate, saltie_game, dataframes)
            for attr, predicate in map_attributes_to_predicates.items()
        }
        return PositionalTendencies(**init_params)

    @staticmethod
    def get_duration_from_predicate(predicate: Callable, saltie_game: 'SaltieGame',
                                    dataframes: Dict[str, pd.DataFrame]):
        boolean_index = predicate(**dataframes)
        deltas = saltie_game.data_frame.game.delta
        goal_frames = saltie_game.data_frame.game.goal_number.notnull()
        return deltas[goal_frames][boolean_index].sum()

    @staticmethod
    def get_flipped_dataframes(dataframes: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        new_dataframes = {
            _k: _v.copy() for _k, _v in dataframes.items()
        }

        for dataframe in new_dataframes.values():
            dataframe.pos_y *= -1
            dataframe.rot_y += 65535 / 2
            dataframe.rot_y %= 65536

        return new_dataframes
