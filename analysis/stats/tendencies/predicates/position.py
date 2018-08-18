import pandas as pd

from ....simulator.map_constants import MAP_Y

"""
All functions here assume the car is on the blue team and the game is played on a standard map.
"""


def get_half_0(player_dataframe: pd.DataFrame, **kwargs):
    # hopefully returns indices that can be used as boolean indexing.
    return player_dataframe.pos_y < 0


def get_half_1(player_dataframe: pd.DataFrame, **kwargs):
    return player_dataframe.pos_y > 0


MAP_THIRD = MAP_Y / 6


def get_third_0(player_dataframe: pd.DataFrame, **kwargs):
    return player_dataframe.pos_y < -MAP_THIRD


def get_third_1(player_dataframe: pd.DataFrame, **kwargs):
    return (-MAP_THIRD < player_dataframe.pos_y) & (player_dataframe.pos_y < MAP_THIRD)


def get_third_2(player_dataframe: pd.DataFrame, **kwargs):
    return player_dataframe.pos_y > MAP_THIRD


HEIGHT_0_LIM = 20  # Height of car when on ground
HEIGHT_1_LIM = 840  # Goal height


def get_height_0(player_dataframe: pd.DataFrame, **kwargs):
    return player_dataframe.pos_z < HEIGHT_0_LIM


def get_height_1(player_dataframe: pd.DataFrame, **kwargs):
    return (HEIGHT_0_LIM < player_dataframe.pos_z) & (player_dataframe.pos_z < HEIGHT_1_LIM)


def get_height_2(player_dataframe: pd.DataFrame, **kwargs):
    return player_dataframe.pos_z > HEIGHT_1_LIM


def get_ball_0(player_dataframe: pd.DataFrame, ball_dataframe: pd.DataFrame):
    return player_dataframe.pos_y < ball_dataframe.pos_y


def get_ball_1(player_dataframe: pd.DataFrame, ball_dataframe: pd.DataFrame):
    return player_dataframe.pos_y > ball_dataframe.pos_y


__all__ = [
    'get_height_0',
    'get_height_1',
    'get_height_2',
    'get_half_0',
    'get_half_1',
    'get_third_0',
    'get_third_1',
    'get_third_2',
    'get_ball_0',
    'get_ball_1',
]
