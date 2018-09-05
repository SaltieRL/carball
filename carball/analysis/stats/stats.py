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
        :param proto_stat:
        :param game:
        :param proto_game:
        :param player_map:
        :param data_frame:
        :return:
        """
        raise NotImplementedError()

    def calculate_player_stat(self, player_stat_map: Dict[str, PlayerStats], game: Game, proto_game: game_pb2.Game,
                              player_map: Dict[str, Player], data_frame: pd.DataFrame):
        """
        Calculates stats that only apply to teams
        :param player_stat_map:
        :param game:
        :param proto_game:
        :param player_map:
        :param data_frame:
        :return:
        """
        raise NotImplementedError()

    def calculate_team_stat(self, team_stat_list: Dict[int, TeamStats], game: Game, proto_game: game_pb2.Game,
                            player_map: Dict[str, Player], data_frame: pd.DataFrame):
        """
        Calculate stats that only applies to a single player
        :param team_stat_list:
        :param game:
        :param proto_game:
        :param player_map:
        :param data_frame:
        :return:
        """
        raise NotImplementedError()


class HitStat:
    def initialize_hit_stat(self, game: Game, player_map: Dict[str, Player], data_frame: pd.DataFrame):
        raise NotImplementedError()

    def calculate_next_hit_stat(self, game: Game, proto_game: game_pb2.Game, saltie_hit: Hit, next_saltie_hit: Hit,
                                player_map: Dict[str, Player]):
        """
        Calculate stats that use only the current hit + the next hit.
        :param game:
        :param proto_game:
        :param saltie_hit:
        :param next_saltie_hit:
        :param player_map:
        :return:
        """
        raise NotImplementedError()
