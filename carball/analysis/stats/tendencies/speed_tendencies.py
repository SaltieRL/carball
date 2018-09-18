from typing import Dict

import pandas as pd

from carball.analysis.stats.utils.panda_utils import return_time_by_truthy_data
from ....analysis.stats.stats import BaseStat
from ....generated.api import game_pb2
from ....generated.api.player_pb2 import Player
from ....generated.api.stats.player_stats_pb2 import PlayerStats
from ....json_parser.game import Game


class SpeedTendencies(BaseStat):

    def calculate_player_stat(self, player_stat_map: Dict[str, PlayerStats], game: Game, proto_game: game_pb2.Game,
                              player_map: Dict[str, Player], data_frame: pd.DataFrame):

        for key, player in player_map.items():
            self.calculate_speed_for_player(player, proto_game, data_frame)

    @classmethod
    def calculate_speed_for_player(cls, player: Player, proto_game: game_pb2.Game, data_frame: pd.DataFrame):
        player_data_frame = data_frame[player.name]

        speed: pd.Series = (player_data_frame.vel_x ** 2 +
                            player_data_frame.vel_y ** 2 +
                            player_data_frame.vel_z ** 2) ** 0.5

        average_speed = speed.mean()

        player.stats.averages.average_speed = average_speed

        fast_frames = speed >= 2200
        result = return_time_by_truthy_data(data_frame, fast_frames)
        player.stats.speed.time_at_super_sonic = result

        slow_frames = speed <= 700
        player.stats.speed.time_at_slow_speed = return_time_by_truthy_data(data_frame, slow_frames)

        boost_frames = speed > 1410
        player.stats.speed.time_at_boost_speed = return_time_by_truthy_data(data_frame, boost_frames)

