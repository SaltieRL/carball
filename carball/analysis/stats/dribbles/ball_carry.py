import logging
from typing import Dict

import numpy as np
import pandas as pd
from carball.analysis.constants.field_constants import FieldConstants

from carball.analysis.stats.utils.pandas_utils import sum_deltas_by_truthy_data
from ....analysis.stats.stats import BaseStat
from ....generated.api import game_pb2
from ....generated.api.player_pb2 import Player
from ....generated.api.stats.player_stats_pb2 import PlayerStats
from ....json_parser.game import Game, BOOST_PER_SECOND

logger = logging.getLogger(__name__)


class CarryStat(BaseStat):
    def calculate_player_stat(self, player_stat_map: Dict[str, PlayerStats], game: Game, proto_game: game_pb2.Game,
                              player_map: Dict[str, Player], data_frame: pd.DataFrame):
        for ball_carry in proto_game.game_stats.ball_carries:
            player_stats = player_stat_map[ball_carry.player_id.id]
            carry_stats = player_stats.carry_dribbles
            carry_stats.total_carries += 1

            # time
            carry_stats.total_carry_time += ball_carry.carry_time
            if carry_stats.longest_carry < ball_carry.carry_time:
                carry_stats.longest_carry = ball_carry.carry_time

            # distance
            carry_stats.total_carry_distance += ball_carry.distance_traveled
            if carry_stats.furthest_carry < ball_carry.distance_traveled:
                carry_stats.furthest_carry = ball_carry.distance_traveled

            if carry_stats.fastest_carry_speed < ball_carry.carry_stats.average_carry_speed:
                carry_stats.fastest_carry_speed = ball_carry.carry_stats.average_carry_speed
