from typing import Dict

import pandas as pd
from carball.generated.api.stats.kickoff_pb2 import KickoffPlayer, TouchPosition, BOOST, CHEAT, GOAL, BALL, AFK

from carball.analysis.stats.stats import BaseStat
from carball.generated.api import game_pb2
from carball.generated.api.player_pb2 import Player
from carball.generated.api.stats.player_stats_pb2 import PlayerStats, CumulativeKickoffStats
from carball.json_parser.game import Game


class KickoffStat(BaseStat):
    def calculate_player_stat(self, player_stat_map: Dict[str, PlayerStats], game: Game, proto_game: game_pb2.Game,
                              player_map: Dict[str, Player], data_frame: pd.DataFrame):
        for kickoff in proto_game.game_stats.kickoff_stats:
            for kickoff_player in kickoff.touch.players:
                if kickoff_player.player.id in player_stat_map:
                    is_first_touch = kickoff.touch.first_touch_player.id == kickoff_player.player.id
                    self.compute_totals(kickoff_player, player_stat_map[kickoff_player.player.id].kickoff_stats, is_first_touch)

        for player_id in player_stat_map:
            kickoff_stats = player_stat_map[player_id].kickoff_stats
            kickoff_stats.average_boost_used = kickoff_stats.average_boost_used / kickoff_stats.total_kickoffs

    def compute_totals(self, kickoff_player: KickoffPlayer,
                       player_kickoff_stats: CumulativeKickoffStats,
                       is_first_touch: bool):
        player_kickoff_stats.total_kickoffs += 1
        if kickoff_player.touch_position == BOOST:
            player_kickoff_stats.num_time_boost += 1
        if kickoff_player.touch_position == CHEAT:
            player_kickoff_stats.num_time_cheat += 1
        if kickoff_player.touch_position == GOAL:
            player_kickoff_stats.num_time_defend += 1
        if kickoff_player.touch_position == BALL:
            player_kickoff_stats.num_time_go_to_ball += 1
        if kickoff_player.touch_position == AFK:
            player_kickoff_stats.num_time_afk += 1
        if is_first_touch:
            player_kickoff_stats.num_time_first_touch += 1

        player_kickoff_stats.average_boost_used += kickoff_player.boost
