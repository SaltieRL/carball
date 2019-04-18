from typing import Dict

import pandas as pd

from carball.analysis.stats.stats import BaseStat
from carball.generated.api import game_pb2
from carball.generated.api.player_pb2 import Player
from carball.generated.api.stats.team_stats_pb2 import TeamStats
from carball.generated.api.stats.rumble_pb2 import PowerUp
from carball.json_parser.game import Game
from carball.analysis.stats.rumble.rumble import is_rumble_enabled


class PreRumbleGoals(BaseStat):

    def calculate_team_stat(self, team_stat_list: Dict[int, TeamStats], game: Game, proto_game: game_pb2.Game,
                            player_map: Dict[str, Player], data_frame: pd.DataFrame):
        if not is_rumble_enabled(game):
            return

        pre_power_up_goals = [0, 0]

        item_get_frames = sorted(set(map(lambda event: event.frame_number_get, proto_game.game_stats.rumble_items)))

        for goal in proto_game.game_metadata.goals:
            # kick off frame before the goal
            kickoff_frame = next(frame for frame in reversed(game.kickoff_frames) if frame < goal.frame_number)

            # first item get frame after kick off
            next_get_frame = next((frame for frame in item_get_frames if frame > kickoff_frame), -1)

            if next_get_frame > goal.frame_number or next_get_frame == -1:
                # goal before rumble items
                pre_power_up_goals[player_map[goal.player_id.id].is_orange] += 1
                goal.rumble_info.pre_items = True
            else:
                goal.rumble_info.pre_items = False

        team_stat_list[0].rumble_stats.pre_item_goals = pre_power_up_goals[0]
        team_stat_list[1].rumble_stats.pre_item_goals = pre_power_up_goals[1]


class ItemGoals(BaseStat):

    def calculate_stat(self, proto_stat, game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player],
                       data_frame: pd.DataFrame):
        if not is_rumble_enabled(game):
            return

        game_df = data_frame['game']

        for goal in proto_game.game_metadata.goals:
            # time of the goal
            goal_time = game_df.loc[goal.frame_number]['time']

            # get the frame number 3 seconds before the goal
            start_frame = game_df.loc[game_df['time'] >= goal_time - 3].index[0]

            player_df = data_frame[player_map[goal.player_id.id].name]
            player_df = player_df.loc[start_frame:goal.frame_number]

            if player_df['power_up_active'].any():
                goal.rumble_info.scored_with_item = True
                goal.rumble_info.used_item = PowerUp.Value(player_df.loc[player_df['power_up_active'] == True]
                                                           .iloc[0]['power_up'].upper())
            else:
                goal.rumble_info.scored_with_item = False
