import logging

import pandas as pd

from ...analysis.cleaner.frame_cleaner import remove_invalid_players
from ...generated.api import game_pb2
from ...json_parser.game import Game


logger = logging.getLogger(__name__)


def clean_replay(game: Game, data_frame: pd.DataFrame, proto_game: game_pb2.Game, player_map):
    drop_nans(data_frame)

    remove_invalid_players(game, data_frame, proto_game, player_map)

    logger.info('cleaned up the replay')


def drop_nans(data_frame: pd.DataFrame):
    data_frame.dropna(axis=1, how='all')
    post_hit = data_frame[(data_frame.game.time > 5.0)]
    columns_to_remove = post_hit.columns[post_hit.isna().all()].tolist()
    if len(columns_to_remove) > 0:
        data_frame.drop(columns_to_remove, axis=1, inplace=True)
        logger.warning('Dropping these columns' + str(columns_to_remove))
