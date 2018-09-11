from typing import Dict

import pandas as pd

from ....analysis.stats.stats import HitStat
from ....generated.api import game_pb2
from ....generated.api.player_pb2 import Player
from ....generated.api.stats.events_pb2 import Hit
from ....json_parser.game import Game


class DistanceStats(HitStat):

    def initialize_hit_stat(self, game: Game, player_map: Dict[str, Player], data_frame: pd.DataFrame):
        pass

    def calculate_next_hit_stat(self, game: Game, proto_game: game_pb2.Game, saltie_hit: Hit, next_saltie_hit: Hit,
                                player_map: Dict[str, Player], hit_index: int):
        player = player_map[saltie_hit.player_id.id]
        hit_distance_y = next_saltie_hit.ball_data.pos_y - saltie_hit.ball_data.pos_y

        if player.is_orange:
            hit_distance_y *= -1

        if hit_distance_y > 0:
            player.stats.distance.ball_hit_forward += hit_distance_y
        if hit_distance_y < 0:
            player.stats.distance.ball_hit_backward += abs(hit_distance_y)
