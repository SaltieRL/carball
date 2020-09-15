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
from ....json_parser.actor.boost import BOOST_PER_SECOND
from ....json_parser.game import Game

logger = logging.getLogger(__name__)


class DemoStat(BaseStat):
    def calculate_player_stat(self, player_stat_map: Dict[str, PlayerStats], game: Game, proto_game: game_pb2.Game,
                              player_map: Dict[str, Player], data_frame: pd.DataFrame):
        player_demo_counts = {}
        player_got_demoed_counts = {}
        for demo in game.demos:
            attacker = demo['attacker'].online_id
            victim = demo['victim'].online_id
            if attacker not in player_demo_counts:
                player_demo_counts[attacker] = 1
            else:
                player_demo_counts[attacker] += 1
            if victim not in player_got_demoed_counts:
                player_got_demoed_counts[victim] = 1
            else:
                player_got_demoed_counts[victim] += 1
        for player in player_demo_counts:
            player_stat_map[player].demo_stats.num_demos_inflicted = player_demo_counts[player]
        for player in player_got_demoed_counts:
            player_stat_map[player].demo_stats.num_demos_taken = player_got_demoed_counts[player]
