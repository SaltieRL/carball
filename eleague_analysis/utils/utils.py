from typing import Sequence, Union

import pandas as pd
import numpy as np

from .columns import PlayerColumn, BallColumn, GameColumn

DataColumn = Union[PlayerColumn, BallColumn, GameColumn]


def flip_teams(df: pd.DataFrame):
    """
    Returns a new df where players' teams are effectively swapped.
    :param df: pd.DataFrame
    :return: the modified-in-place input pd.DataFrame
    """
    _df = df.copy()
    players = [
        name for name in _df.columns.get_level_values(level=0).unique()
        if name != 'ball' and name != 'game'
    ]
    for player in players:
        _df.loc[:, (player, 'pos_x')] *= -1
        _df.loc[:, (player, 'pos_y')] *= -1
        _df.loc[:, (player, 'vel_x')] *= -1
        _df.loc[:, (player, 'vel_y')] *= -1
        _df.loc[:, (player, 'rot_z')] += np.pi

    _df.loc[:, ('ball', 'pos_x')] *= -1
    _df.loc[:, ('ball', 'pos_y')] *= -1
    _df.loc[:, ('ball', 'vel_x')] *= -1
    _df.loc[:, ('ball', 'vel_y')] *= -1
    return _df


def filter_columns(df: pd.DataFrame, columns: Sequence[DataColumn]):
    """
    Returns a new pd.DataFrame only containing the given columns.
    :param df: Replay's df to filter
    :param columns: Sequence of DataColumns to keep
    :return: new pd.DataFrame
    """
    player_df = df.drop(columns=['ball', 'game'], level=0)
    ball_df = df.xs('ball', level=0, axis=1, drop_level=False)
    game_df = df.xs('game', level=0, axis=1, drop_level=False)

    player_columns = [column.value for column in columns if isinstance(column, PlayerColumn)]
    ball_columns = [column.value for column in columns if isinstance(column, BallColumn)]
    game_columns = [column.value for column in columns if isinstance(column, GameColumn)]

    filtered_player_df = player_df.loc[:, (slice(None), player_columns)]
    filtered_ball_df = ball_df.loc[:, (slice(None), ball_columns)]
    filtered_game_df = game_df.loc[:, (slice(None), game_columns)]

    return pd.concat([filtered_player_df, filtered_ball_df, filtered_game_df], axis=1)


NORMALISATION_FACTORS = {
    'pos_x': 4096,
    'pos_y': 6000,
    'pos_z': 2048,
    'rot_x': np.pi,
    'rot_y': np.pi,
    'rot_z': np.pi,
    'vel_x': 23000,
    'vel_y': 23000,
    'vel_z': 23000,
    'ang_vel_x': 5500,
    'ang_vel_y': 5500,
    'ang_vel_z': 5500,
    'throttle': 255,
    'steer': 255,
    'boost': 255,
}


def normalise_df(df: pd.DataFrame, inplace: bool = False):
    if not inplace:
        df = df.copy()
    for column, normalisation_factor in NORMALISATION_FACTORS.items():
        df.loc[:, (slice(None), column)] /= normalisation_factor
    return df
