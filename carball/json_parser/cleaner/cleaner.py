import logging

import pandas as pd

from ...generated.api import game_pb2
from ...json_parser.game import Game
from ...json_parser.cleaner.frame_cleaner import remove_invalid_players


logger = logging.getLogger(__name__)


def clean_replay(game: Game, data_frame: pd.DataFrame, proto_game: game_pb2.Game, player_map):
    try:
        remove_invalid_players(game, data_frame, proto_game, player_map)
    except:
        logger.warning('Unable to clean invalid players')
