from typing import Dict

import pandas as pd

from carball.analysis.stats.stats import BaseStat
from carball.generated.api import game_pb2
from carball.generated.api.player_pb2 import Player
from carball.generated.api.stats.team_stats_pb2 import TeamStats
from carball.json_parser.game import Game
from carball.generated.api.metadata.game_metadata_pb2 import RANKED_RUMBLE, UNRANKED_RUMBLE


class PreRumbleGoals(BaseStat):

    def calculate_team_stat(self, team_stat_list: Dict[int, TeamStats], game: Game, proto_game: game_pb2.Game,
                            player_map: Dict[str, Player], data_frame: pd.DataFrame):
        if game.game_info.playlist not in [RANKED_RUMBLE, UNRANKED_RUMBLE]:
            return

        pre_power_up_goals = (0, 0)

        item_get_frames = sorted(set(map(lambda event: event.frame_number_get, proto_game.game_stats.rumble_items)))

        for goal in game.goals:
            # kick off frame before the goal
            kickoff_frame = next(frame for frame in reversed(game.kickoff_frames) if frame < goal.frame_number)

            # first item get frame after kick off
            next_get_frame = next(frame for frame in item_get_frames if frame > kickoff_frame)

            if next_get_frame > goal.frame_number:
                # goal before rumble items
                pre_power_up_goals[goal.player_team] += 1

        team_stat_list[0].rumble_stats.pre_item_goals = pre_power_up_goals[0]
        team_stat_list[1].rumble_stats.pre_item_goals = pre_power_up_goals[1]
