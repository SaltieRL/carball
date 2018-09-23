import logging

import pandas as pd

from ...generated.api import game_pb2
from ...json_parser.game import Game


logger = logging.getLogger(__name__)


def remove_invalid_players(game: Game, data_frame: pd.DataFrame, proto_game: game_pb2.Game, player_map):
    invalid_players = []
    for player in proto_game.players:
        name = player.name
        if player.time_in_game < 5 or name not in data_frame or ('pos_x' not in data_frame[name]):
            invalid_players.append(player.name)
    if len(invalid_players) == 0:
        return

    # remove from game
    game.players = [player for player in game.players if player.name not in invalid_players]

    # remove from protobuf
    proto_players = proto_game.players
    i = 0
    total_length = len(proto_players)

    while i < total_length:
        player = proto_players[i]
        if player.name in invalid_players:
            del player_map[player.id.id]
            del proto_players[i]
            i -= 1
            total_length -= 1
        i += 1
    logger.warning('removed player: ' + str(invalid_players))
