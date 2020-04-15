import logging

import pandas as pd

from ...generated.api import game_pb2
from ...json_parser.game import Game


logger = logging.getLogger(__name__)


def remove_invalid_players(game: Game, data_frame: pd.DataFrame, proto_game: game_pb2.Game, player_map):
    """
    Finds and removes invalid players from all relevant fields.

    :param game: The Game object.
    :param data_frame: The pandas.DataFrame object.
    :param proto_game: The game's protobuf object.
    :param player_map: The map of players' online IDs to the Player objects.
    """

    # Get invalid players; if none - return.
    invalid_players = get_invalid_players(proto_game, data_frame)
    if len(invalid_players) == 0:
        return

    # Remove player from Game and game_pb2.Game
    game.players = [player for player in game.players if player.name not in invalid_players]
    remove_player_from_protobuf(proto_game, player_map, invalid_players)

    logger.warning("Invalid player(s) removed: " + str(invalid_players))


def get_invalid_players(proto_game: game_pb2.Game, data_frame: pd.DataFrame):
    """
    :return: An array of invalid players' names.
    """

    invalid_players = []
    for player in proto_game.players:
        name = player.name
        if player.time_in_game < 5 or name not in data_frame or ('pos_x' not in data_frame[name]):
            invalid_players.append(player.name)

    return invalid_players


def remove_player_from_protobuf(proto_game: game_pb2.Game, player_map, invalid_players):
    """
    Removes invalid players from all relevant proto_game fields.
    """

    proto_players = proto_game.players
    i = 0
    total_length = len(proto_players)

    while i < total_length:
        player = proto_players[i]
        if player.name in invalid_players:
            del player_map[player.id.id]
            del proto_players[i]

            remove_player_from_team(proto_game, player)

            i -= 1
            total_length -= 1
        i += 1


def remove_player_from_team(proto_game: game_pb2.Game, player):
    """
    Removes given player from proto_game.teams
    """

    for team in proto_game.teams:
        for i in range(len(team.player_ids)):
            if team.player_ids[i] == player.id:
                del team.player_ids[i]
                break
