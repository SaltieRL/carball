import pandas as pd


def sum_deltas_by_player_name(data_frame: pd.DataFrame, players_data_frame: pd.Series) -> pd.DataFrame:
    """
    Gets the delta from the pandas data frame for certain players at certain times
    :param data_frame: The game data frame, goal frames are removed
    :param players_data_frame: Just the players
    :return: The time based on delta.
    """
    combined_data = pd.concat([players_data_frame, data_frame['game', 'delta'].rename('delta')], axis=1)
    return combined_data.groupby(players_data_frame.name).sum().rename(columns={'delta': players_data_frame.name})


def sum_deltas_by_truthy_data(data_frame: pd.DataFrame, truthy_frames: pd.Series) -> pd.DataFrame:
    """
    Gets the delta from the pandas data frame for certain players at certain times.
    :param data_frame: The game data frame, goal frames are removed
    :param truthy_frames: Frames that have a truth value applied to them.
    :return: The time based on delta.
    """
    truthy_frames = truthy_frames.rename('truthy')
    combined_data = pd.concat([truthy_frames, data_frame['game', 'delta'].rename('delta')], axis=1)
    return combined_data.loc[combined_data['truthy'] == True].sum().rename(columns={'delta': 'true_values'}).delta
