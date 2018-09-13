import logging
from typing import Dict

import pandas as pd

from ...generated.api import game_pb2
from ...generated.api.player_pb2 import Player
from ...generated.api.stats.events_pb2 import Hit
from ...generated.api.stats.player_stats_pb2 import PlayerStats
from ...generated.api.stats.team_stats_pb2 import TeamStats
from ...json_parser.game import Game


class BaseStat:

    def __init__(self):
        self.logger = logging.getLogger(type(self).__name__)

    def calculate_stat(self, proto_stat, game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player],
                       data_frame: pd.DataFrame):
        """
        Calculates stats that applies to the general game or applies to players + teams at the same time.
        :param proto_stat: This is protobuf object for general game stats
        :param game: The raw data that has been created from python.
        :param proto_game: A protobuf that contains some parsed stats + all metadata for the game.
        :param player_map: A map of playerId to the protobuf Player object
        :param data_frame: The raw frames of the replay this is the same object as `game.frames`
        """
        raise NotImplementedError()

    def calculate_player_stat(self, player_stat_map: Dict[str, PlayerStats], game: Game, proto_game: game_pb2.Game,
                              player_map: Dict[str, Player], data_frame: pd.DataFrame):
        """
        Calculates stats that only apply to players.
        :param player_stat_map: A map of playerId to the specific proto object for stats for that player.
        :param game: The raw data that has been created from python.
        :param proto_game: A protobuf that contains some parsed stats + all metadata for the game.
        :param player_map: A map of playerId to the protobuf Player object
        :param data_frame: The raw frames of the replay this is the same object as `game.frames`
        """
        raise NotImplementedError()

    def calculate_team_stat(self, team_stat_list: Dict[int, TeamStats], game: Game, proto_game: game_pb2.Game,
                            player_map: Dict[str, Player], data_frame: pd.DataFrame):
        """
        Calculate stats that only applies to teams
        :param team_stat_list: I map of team id to the specific proto object for stats for that team
        :param game: The raw data that has been created from python.
        :param proto_game: A protobuf that contains some parsed stats + all metadata for the game.
        :param player_map: A map of playerId to the protobuf Player object
        :param data_frame: The raw frames of the replay this is the same object as `game.frames`
        """
        raise NotImplementedError()


class HitStat:
    def initialize_hit_stat(self, game: Game, player_map: Dict[str, Player], data_frame: pd.DataFrame):
        """
        Called only once at the beginning of stat creation.
        :param game: The raw data that has been created from python.
        :param player_map: A map of playerId to the protobuf Player object
        :param data_frame: The raw frames of the replay this is the same object as `game.frames`
        """
        raise NotImplementedError()

    def calculate_next_hit_stat(self, game: Game, proto_game: game_pb2.Game, saltie_hit: Hit, next_saltie_hit: Hit,
                                player_map: Dict[str, Player], hit_index: int):
        """
        Calculate stats that use only the current hit + the next hit.
        :param game: The raw data that has been created from python.
        :param proto_game: A protobuf that contains some parsed stats + all metadata for the game.
        :param saltie_hit: The current hit we are looking at, this is a protobuf object.
        :param next_saltie_hit:  The hit that occured after the current one.
        :param player_map: A map of playerId to the protobuf Player object
        :param hit_index: The index in the list of protobuf hits where the current hit is listed.
        """
        raise NotImplementedError()
