from typing import Dict

import pandas

from carball.analysis.stats.stats import HitStat
from carball.generated.api import game_pb2
from carball.generated.api.player_pb2 import Player
from carball.generated.api.stats import stats_pb2
from carball.generated.api.stats.events_pb2 import Hit
from carball.json_parser.game import Game


class HitCountStat(HitStat):

    def initialize_hit_stat(self, game: Game, player_map: Dict[str, Player], data_frame: pandas.DataFrame):
        pass

    def apply_stat(self, hit_count: stats_pb2.HitCounts, saltie_hit):
        if saltie_hit.dribble:
            hit_count.total_dribbles += 1
        if saltie_hit.dribble_continuation:
            hit_count.total_dribble_conts += 1
        if saltie_hit.pass_:
            hit_count.total_passes += 1
        if saltie_hit.goal:
            hit_count.total_goals += 1
        if saltie_hit.shot:
            hit_count.total_shots += 1
        if saltie_hit.save:
            hit_count.total_saves += 1
        if saltie_hit.aerial:
            hit_count.total_aerials += 1
        hit_count.total_hits += 1

    def calculate_next_hit_stat(self, game: Game, proto_game: game_pb2.Game, saltie_hit: Hit, next_saltie_hit: Hit,
                                player_map: Dict[str, Player], hit_index: int):
        player = player_map[saltie_hit.player_id.id]
        self.apply_stat(player.stats.hit_counts, saltie_hit)
        team = proto_game.teams[player.is_orange]
        self.apply_stat(team.stats.hit_counts, saltie_hit)
