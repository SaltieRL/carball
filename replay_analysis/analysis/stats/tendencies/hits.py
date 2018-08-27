from typing import Dict

from replay_analysis.analysis.stats.stats import BaseStat
from replay_analysis.generated.api import game_pb2
from replay_analysis.generated.api.player_pb2 import Player
from replay_analysis.generated.api.stats.player_stats_pb2 import PlayerStats
from replay_analysis.json_parser.game import Game
from .averages import Averages
from .positional_tendencies import PositionalTendencies


class HitsStat(BaseStat):
    def __init__(self):
        self.tendencies = PositionalTendencies()

    def calculate_player_stat(self, player_stat_map: Dict[str, PlayerStats], game: Game, proto_game: game_pb2.Game,
                              player_map: Dict[str, Player], data_frames):

        for id, player in player_map.items():
            # analysis stuff
            player_hits = [h for h in proto_game.game_stats.hits if h.player_id.id == player.id.id]

            # and not (h.dribble or h.dribble_continuation)])
            hits = len(player_hits)
            player.stats.hits.hits = hits
            analytics = {'dribbles': 0, 'dribble_conts': 0, 'passes': 0, 'shots': 0, 'goals': 0, 'saves': 0}
            for h in player_hits:
                if h.dribble:
                    analytics['dribbles'] += 1
                if h.dribble_continuation:
                    analytics['dribble_conts'] += 1
                if h.pass_:
                    analytics['passes'] += 1
                if h.goal:
                    analytics['goals'] += 1
                if h.shot:
                    analytics['shots'] += 1
                if h.save:
                    analytics['saves'] += 1
            for k in analytics:
                setattr(player.stats.hits, k, analytics[k])
