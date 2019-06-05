import logging
from typing import Dict

import pandas as pd
from ....analysis.stats.stats import BaseStat
from ....generated.api import game_pb2
from ....generated.api.player_pb2 import Player
from ....generated.api.stats.player_stats_pb2 import PlayerStats
from ....json_parser.game import Game

logger = logging.getLogger(__name__)


class CarryStat(BaseStat):
    def calculate_player_stat(self, player_stat_map: Dict[str, PlayerStats], game: Game, proto_game: game_pb2.Game,
                              player_map: Dict[str, Player], data_frame: pd.DataFrame):
        for event_carry in proto_game.game_stats.ball_carries:
            player_stats = player_stat_map[event_carry.player_id.id]
            player_carry_stats = player_stats.ball_carries
            player_carry_stats.total_carries += 1
            if event_carry.has_flick:
                player_carry_stats.total_flicks += 1

            # time
            player_carry_stats.total_carry_time += event_carry.carry_time
            if player_carry_stats.longest_carry < event_carry.carry_time:
                player_carry_stats.longest_carry = event_carry.carry_time

            # distance
            player_carry_stats.total_carry_distance += event_carry.straight_line_distance
            if player_carry_stats.furthest_carry < event_carry.straight_line_distance:
                player_carry_stats.furthest_carry = event_carry.straight_line_distance

            if player_carry_stats.fastest_carry_speed < event_carry.carry_stats.average_carry_speed:
                player_carry_stats.fastest_carry_speed = event_carry.carry_stats.average_carry_speed
            self.add_ball_stats(player_carry_stats.carry_stats, event_carry.carry_stats)

        for player_key in player_stat_map:
            player_carry_stats = player_stat_map[player_key].ball_carries
            num_carries = player_carry_stats.total_carries
            if num_carries == 0:
                continue
            player_carry_stats.average_carry_time = player_carry_stats.total_carry_time / num_carries
            self.average_ball_stats(player_carry_stats.carry_stats, num_carries)

    def add_ball_stats(self, player_carry, event_carry):
        player_carry.average_z_distance += event_carry.average_z_distance
        player_carry.average_xy_distance += event_carry.average_xy_distance
        player_carry.average_ball_z_velocity += event_carry.average_ball_z_velocity
        player_carry.variance_xy_distance += event_carry.variance_xy_distance
        player_carry.variance_z_distance += event_carry.variance_z_distance
        player_carry.variance_ball_z_velocity += event_carry.variance_ball_z_velocity
        player_carry.average_carry_speed += event_carry.average_carry_speed
        player_carry.distance_along_path += event_carry.distance_along_path

    def average_ball_stats(self, player_carry, num_carries):
        player_carry.average_z_distance /= num_carries
        player_carry.average_xy_distance /= num_carries
        player_carry.average_ball_z_velocity /= num_carries
        player_carry.variance_xy_distance /= num_carries
        player_carry.variance_z_distance /= num_carries
        player_carry.variance_ball_z_velocity /= num_carries
        player_carry.average_carry_speed /= num_carries
        player_carry.distance_along_path /= num_carries
