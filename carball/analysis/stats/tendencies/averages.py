from typing import List, Dict
import pandas as pd
from ....analysis.stats.stats import BaseStat

from ....generated.api import game_pb2
from ....generated.api.player_pb2 import Player
from ....generated.api.stats.events_pb2 import Hit
from ....generated.api.stats.player_stats_pb2 import PlayerStats
from ....json_parser.game import Game


class Averages(BaseStat):
    def calculate_player_stat(self, player_stat_map: Dict[str, PlayerStats], game: Game, proto_game: game_pb2.Game,
                              player_map: Dict[str, Player], data_frame: pd.DataFrame):

        for key, player in player_map.items():
            self.get_averages_for_player(player, proto_game, data_frame)

    @classmethod
    def get_averages_for_player(cls, player: Player, proto_game: game_pb2.Game, data_frame: pd.DataFrame):
        player_hits: List[Hit] = [saltie_hit for saltie_hit in proto_game.game_stats.hits if
                                  saltie_hit.player_id == player.id]

        hit_distances = [saltie_hit.distance for saltie_hit in player_hits
                         if saltie_hit.distance is not None and not saltie_hit.dribble]
        if len(hit_distances) > 0:
            average_hit_distance = sum(hit_distances) / len(hit_distances)
            player.stats.averages.average_hit_distance = average_hit_distance
