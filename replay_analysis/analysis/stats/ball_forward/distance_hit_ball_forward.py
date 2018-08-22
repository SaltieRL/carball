from typing import Dict

from replay_analysis.analysis.stats.stats import HitStat
from replay_analysis.generated.api.player_pb2 import Player
from replay_analysis.generated.api.stats.events_pb2 import Hit
from replay_analysis.json_parser.game import Game


class DistanceStats(HitStat):

    def initialize_hit_stat(self, game: Game, player_map: Dict[str, Player], data_frames):
        pass

    def calculate_next_hit_stat(self, game: Game, saltie_hit: Hit, next_saltie_hit: Hit, player_map: Dict[str, Player]):
        player = player_map[saltie_hit.player_id.id]
        hit_distance_y = next_saltie_hit.ball_data.pos_y - saltie_hit.ball_data.pos_y

        if player.is_orange:
            hit_distance_y *= -1

        if hit_distance_y > 0:
            player.stats.distance.forward = player.stats.distance.forward + hit_distance_y
        if hit_distance_y < 0:
            player.stats.distance.backward = player.stats.distance.backward + abs(hit_distance_y)
