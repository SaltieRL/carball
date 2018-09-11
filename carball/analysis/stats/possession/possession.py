from typing import Dict

import pandas as pd

from ....analysis.stats.stats import BaseStat, HitStat
from ....generated.api import game_pb2
from ....generated.api.player_pb2 import Player
from ....generated.api.stats.events_pb2 import Hit
from ....generated.api.stats.team_stats_pb2 import TeamStats
from ....json_parser.game import Game


class PossessionStat(BaseStat, HitStat):
    def __init__(self):
        self.frame_possession_time_deltas = None

    def calculate_team_stat(self, team_stat_list: Dict[int, TeamStats], game: Game,
                            proto_game: game_pb2.Game, player_map: Dict[str, Player],
                            data_frame: pd.DataFrame):
        frame_possession_time_deltas = pd.concat(
            [
                data_frame['ball', 'hit_team_no'],
                data_frame['game', 'delta']
            ],
            axis=1
        )
        frame_possession_time_deltas.columns = ['hit_team_no', 'delta']

        last_hit_possession = frame_possession_time_deltas.groupby('hit_team_no').sum()

        for index, stat in team_stat_list.items():
            stat.possession.possession_time = float(last_hit_possession.delta.loc[index])

    def initialize_hit_stat(self, game: Game, player_map: Dict[str, Player], data_frame: pd.DataFrame):
        self.frame_possession_time_deltas = pd.concat(
            [
                data_frame['ball', 'hit_team_no'],
                data_frame['game', 'delta']
            ],
            axis=1
        )
        self.frame_possession_time_deltas.columns = ['hit_team_no', 'delta']

    def calculate_next_hit_stat(self, game: Game, proto_game: game_pb2.Game, saltie_hit: Hit, next_saltie_hit: Hit,
                                player_map: Dict[str, Player], hit_index: int):
        player = player_map[saltie_hit.player_id.id]
        next_player = player_map[next_saltie_hit.player_id.id]
        if player.is_orange == next_player.is_orange:
            hit_possession_time = self.frame_possession_time_deltas.delta.loc[
                                  saltie_hit.frame_number:next_saltie_hit.frame_number].sum()
            player.stats.possession.possession_time = player.stats.possession.possession_time + hit_possession_time
        else:
            hit_possession_time = self.frame_possession_time_deltas.delta.loc[
                                  saltie_hit.frame_number:next_saltie_hit.frame_number].sum()
            player.stats.possession.possession_time = player.stats.possession.possession_time + hit_possession_time
            proto_game.game_stats.neutral_possession_time = proto_game.game_stats.neutral_possession_time + hit_possession_time
