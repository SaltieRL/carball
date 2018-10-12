import pandas as pd
import numpy as np

position_column_names = ['pos_x', 'pos_y', 'pos_z']
positional_columns = ['pos_x', 'pos_y', 'pos_z', 'rot_x', 'rot_y', 'rot_z']

def get_player_ball_displacements(data_frame: pd.DataFrame, player_name: str) -> pd.DataFrame:
    player_df = data_frame[player_name]
    ball_df = data_frame['ball']

    return get_position_displacements(player_df, ball_df)


def get_position_displacements(data_frame1: pd.DataFrame, data_frame2: pd.DataFrame) -> pd.DataFrame:
    result = data_frame1[position_column_names] - data_frame2[position_column_names]
    return result


def get_distance_from_displacements(data_frame: pd.DataFrame) -> pd.Series:
    positions = data_frame[position_column_names]

    summed = (positions ** 2).sum(axis=1, skipna=False)
    return np.sqrt(summed)
