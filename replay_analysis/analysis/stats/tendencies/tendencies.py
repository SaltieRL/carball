from typing import Dict

from replay_analysis.analysis.stats.stats import BaseStat
from replay_analysis.generated.api import game_pb2
from replay_analysis.generated.api.player_pb2 import Player
from replay_analysis.generated.api.stats.player_stats_pb2 import PlayerStats
from replay_analysis.json_parser.game import Game
from .averages import Averages
from .positional_tendencies import PositionalTendencies


class TendenciesStat(BaseStat):
    def __init__(self):
        self.tendencies = PositionalTendencies()

    def calculate_player_stat(self, player_stat_map: Dict[str, PlayerStats], game: Game, proto_game: game_pb2.Game,
                              player_map: Dict[str, Player], data_frames):

        for id, player in player_map.items():
            self.tendencies.get_player_tendencies(player, data_frames)
            Averages.get_averages_for_player(player, proto_game, data_frames)
