import math
import logging
from typing import Dict

import pandas as pd

from carball.analysis.stats.stats import BaseStat
from carball.generated.api.player_pb2 import Player
from carball.generated.api import game_pb2
from carball.json_parser.game import Game
from carball.analysis.stats.dropshot import is_dropshot
from carball.analysis.constants.dropshot import *

log = logging.getLogger(__name__)


class DropshotGoals(BaseStat):
    def calculate_stat(self, proto_stat, game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player],
                       data_frame: pd.DataFrame):
        if not is_dropshot(game):
            return

        tile_positions = get_tile_positions(game.map)

        if tile_positions is None:
            log.warning(f'Unsupported dropshot map: {game.map}')
            return

        for goal in proto_game.game_metadata.goals:
            frame = goal.frame_number

            # get the ball position at goal
            ball_pos = data_frame['ball'].loc[frame].loc[['pos_x', 'pos_y', 'pos_z']]

            # get the closest tile
            team = player_map[goal.player_id.id].is_orange
            closest_distance = TILE_DIAMETER
            closest_id = -1

            team_tiles = tile_positions[:70] if team == 1 else tile_positions[70:]

            for tile_id, tile in enumerate(team_tiles):

                d = math.sqrt(
                    math.pow(ball_pos['pos_x'] - tile[0], 2) +
                    math.pow(ball_pos['pos_y'] - tile[1], 2) +
                    math.pow(ball_pos['pos_z'] - tile[2], 2)
                )

                if d < closest_distance:
                    closest_distance = d
                    closest_id = tile_id if team == 1 else tile_id + 70

            if closest_id != -1:
                goal.extra_mode_info.dropshot_tile.id = closest_id
