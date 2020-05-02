import logging

import pandas as pd

from ...analysis.cleaner.frame_cleaner import remove_invalid_players
from ...generated.api import game_pb2
from ...json_parser.game import Game


logger = logging.getLogger(__name__)


def clean_replay(game: Game, data_frame: pd.DataFrame, proto_game: game_pb2.Game, player_map):
    """
    Cleans the replay's pandas.DataFrame object, by removing unnecessary/useless values.

    :param game: The Game object.
    :param data_frame: The pandas.DataFrame object.
    :param proto_game: The game's protobuf object.
    :param player_map: The map of players' online IDs to the Player objects.
    """

    # Remove empty columns.
    drop_nans(data_frame)

    # Remove players with missing data.
    remove_invalid_players(game, data_frame, proto_game, player_map)

    logger.info("Replay cleaned.")


def drop_nans(data_frame: pd.DataFrame):
    """
    Removes empty columns. Most commonly the is_overtime column (for games without OT).

    :param data_frame: The pandas.DataFrame object.
    """

    data_frame.dropna(axis=1, how='all')
    post_hit = data_frame[(data_frame.game.time > 5.0)]
    columns_to_remove = post_hit.columns[post_hit.isna().all()].tolist()
    if len(columns_to_remove) > 0:
        data_frame.drop(columns_to_remove, axis=1, inplace=True)
        logger.warning('Dropping these columns' + str(columns_to_remove))
