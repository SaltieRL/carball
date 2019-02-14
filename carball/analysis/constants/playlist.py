from carball.generated.api.game_pb2 import Game

from carball.generated.api.metadata.game_metadata_pb2 import Playlist

from carball.generated.api.metadata import game_metadata_pb2


def get_team_size_from_playlist(playlist: Playlist):
    """
    Returns number of teams in the playlist.
    5 if it is unknown otherwise it will return a valid value.
    :param playlist:
    :return:
    """
    if (playlist == game_metadata_pb2.RANKED_DOUBLES or
            playlist == game_metadata_pb2.UNRANKED_DOUBLES or
            playlist == game_metadata_pb2.RANKED_HOOPS or
            playlist == game_metadata_pb2.UNRANKED_HOOPS):
        return 2

    if playlist == game_metadata_pb2.RANKED_DUELS or playlist == game_metadata_pb2.UNRANKED_DUELS:
        return 1

    if playlist == game_metadata_pb2.UNRANKED_CHAOS:
        return 4

    if playlist == game_metadata_pb2.CUSTOM_LOBBY or playlist == game_metadata_pb2.OFFLINE_SPLITSCREEN:
        return 5

    return 3


def get_playlist_from_game(proto_game: Game):
    return proto_game.game_metadata.playlist


def get_team_size_from_game(proto_game: Game):
    return get_team_size_from_playlist(get_playlist_from_game(proto_game))
