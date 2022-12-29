import logging
from typing import Dict, Callable

import numpy
import pandas as pd

from carball.analysis.stats.utils.pandas_utils import sum_deltas_start_end_frame
from carball.generated.api import game_pb2
from carball.generated.api.metadata.game_metadata_pb2 import Goal
from carball.generated.api.player_pb2 import Player
from carball.generated.api.stats.kickoff_pb2 import KickoffStats
from carball.generated.api.stats import kickoff_pb2 as kickoff
from carball.json_parser.game import Game


logger = logging.getLogger(__name__)


class BaseKickoff:

    @staticmethod
    def get_kickoffs_from_game(game: Game, proto_game: game_pb2, id_creation:Callable,
                               player_map: Dict[str, Player],
                               data_frame: pd.DataFrame, kickoff_frames: pd.DataFrame,
                               first_touch_frames: pd.DataFrame) -> Dict[int, KickoffStats]:
        kickoffs = dict()
        goals = proto_game.game_metadata.goals
        num_goals = len(goals)
        last_frame = data_frame.last_valid_index()
        first_frame = data_frame.first_valid_index()
        for index, frame in enumerate(kickoff_frames):
            starting_kickoff_time = data_frame.game.time[frame]
            cur_kickoff = proto_game.game_stats.kickoff_stats.add()
            end_frame = first_touch_frames[index]
            smaller_data_frame = data_frame.loc[max(first_frame, frame - 1):  min(end_frame + 20, last_frame)]
            cur_kickoff.start_frame = frame
            cur_kickoff.touch_frame = end_frame
            ending_time = smaller_data_frame['game']['time'][end_frame]
            time = cur_kickoff.touch_time = ending_time - starting_kickoff_time
            differs = smaller_data_frame['game']['time'][frame:end_frame].diff()
            summed_time_diff = differs.sum()
            summed_time = smaller_data_frame['game']['delta'][frame:end_frame].sum()
            if summed_time > 0:
                cur_kickoff.touch_time = summed_time
            logger.info("STRAIGHT TIME " + str(time))
            logger.info("SUM TIME" + str(summed_time))
            sum_vs_adding_diff = time - summed_time


            # find who touched the ball first
            closest_player_distance = 10000000
            closest_player_id = 0

            if index < num_goals:
                BaseKickoff.get_goal_data(cur_kickoff, goals[index], data_frame)

            # get player stats
            for player in player_map.values():
                if player.name not in data_frame:
                    continue
                kickoff_player = BaseKickoff.get_player_stats(cur_kickoff, player, smaller_data_frame, frame, end_frame)

                if kickoff_player.ball_dist < closest_player_distance:
                    closest_player_distance = kickoff_player.ball_dist
                    closest_player_id = player.id.id

            if closest_player_distance != 10000000:
                # Todo use hit analysis
                cur_kickoff.touch.first_touch_player.id = closest_player_id
            cur_kickoff.type = BaseKickoff.get_kickoff_type(cur_kickoff.touch.players)
            kickoffs[frame] = cur_kickoff
        return kickoffs

    @staticmethod
    def get_player_stats(cur_kickoff, player, data_frame: pd.DataFrame, start_frame: int, end_frame: int):

        kickoff_player = cur_kickoff.touch.players.add()
        kickoff_player.player.id = player.id.id

        kickoff_player.kickoff_position, kickoff_player.start_left = BaseKickoff.get_kickoff_position(player,
                                                                                                      data_frame,
                                                                                                      start_frame)

        kickoff_player.touch_position = BaseKickoff.get_touch_position(player, data_frame, start_frame, end_frame)
        kickoff_player.boost = data_frame[player.name]['boost'][end_frame]
        kickoff_player.ball_dist = BaseKickoff.get_dist(data_frame, player.name, end_frame)
        kickoff_player.player_position.pos_x = data_frame[player.name]['pos_x'][end_frame]
        kickoff_player.player_position.pos_y = data_frame[player.name]['pos_y'][end_frame]
        kickoff_player.player_position.pos_z = data_frame[player.name]['pos_z'][end_frame]

        kickoff_player.start_position.pos_x = data_frame[player.name]['pos_x'][start_frame]
        kickoff_player.start_position.pos_y = data_frame[player.name]['pos_y'][start_frame]
        kickoff_player.start_position.pos_z = data_frame[player.name]['pos_z'][start_frame]
        BaseKickoff.set_jumps(kickoff_player, player, data_frame, start_frame)
        return kickoff_player

    @staticmethod
    def set_jumps(kPlayer, player, data_frame, frame):
        jump_active_df        = data_frame[player.name]['jump_active']
        if 'boost_collect' in data_frame[player.name].keys():
            collected_boost_df    = data_frame[player.name]['boost_collect']
            collected_boost_df = collected_boost_df[collected_boost_df > 34]
            if len(collected_boost_df) > 0:
                kPlayer.boost_time = data_frame['game']['delta'][frame:collected_boost_df.index.values[0]].sum()

        # Make sure that we are not doing diffs on booleans
        jump_active_df = jump_active_df.astype(float)

        # check the kickoff frames (and then some) for jumps & big boost collection
        jump_active_df = jump_active_df[jump_active_df.diff(1) > 0]
        BaseKickoff.add_jumps(kPlayer, data_frame, frame, jump_active_df)

        """for f in range(frame, )):
            if boost:
                if collected_boost_df[f] == True:
                    
            if jump_active_df[f] != jump_active_df[f-1] or double_jump_active_df[f] != double_jump_active_df[f-1]:
                kPlayer.jumps.append(data_frame['game']['delta'][frame:f].sum())"""

    @staticmethod
    def add_jumps(kPlayer, data_frame, frame, jumps):
        pass

    @staticmethod
    def get_kickoff_type(players: list):
        #
        diagonals = [player.kickoff_position for player in players].count(0)
        offcenter = [player.kickoff_position for player in players].count(1)
        goalies   = [player.kickoff_position for player in players].count(2)
        if len(players) == 6:
            # 3's
            if diagonals == 4:
                if offcenter == 2:
                    return kickoff.THREES_DIAG_DIAG_OFFCENT
                if goalies == 2:
                    return kickoff.THREES_DIAG_DIAG_GOAL
            if diagonals == 2:
                if offcenter == 4:
                    return kickoff.THREES_DIAG_OFFCENT_OFFCENT
                if offcenter == 2:
                    return kickoff.THREES_DIAG_OFFCENT_GOAL
            if offcenter == 4:
                return kickoff.THREES_OFFCENT_OFFCENT_GOAL
        if len(players) == 4:
            if diagonals == 4:
                return kickoff.TWOS_DIAG_DIAG
            if diagonals == 2:
                if offcenter == 2:
                    return kickoff.TWOS_DIAG_OFFCENT
                if goalies == 2:
                    return kickoff.TWOS_DIAG_GOAL
            if offcenter == 4:
                return kickoff.TWOS_OFFCENT_OFFCENT
            if offcenter == 2:
                if goalies == 2:
                    return kickoff.TWOS_OFFCENT_GOAL
        if len(players) == 2:
            if diagonals == 2:
                return kickoff.DUEL_DIAG
            if offcenter == 2:
                return kickoff.DUEL_OFFCENT
            if goalies == 2:
                return kickoff.DUEL_GOAL
        return kickoff.UNKNOWN_KICKOFF_TYPE

    @staticmethod
    def get_kickoff_position(player_class: Player, data_frame: pd.DataFrame, frame: int):
        player = player_class.name
        player_df = data_frame[player]
        pos_x = player_df['pos_x'][frame]
        start_left = not ((pos_x < 0) ^ player_class.is_orange)
        kickoff_position = kickoff.UNKNOWN_KICKOFF_POS
        if abs(abs(pos_x) - 2050) < 100:
            kickoff_position = kickoff.DIAGONAL
        elif abs(abs(pos_x) - 256) < 100:
            kickoff_position = kickoff.OFFCENTER
        elif abs(abs(pos_x)) < 4:
            kickoff_position = kickoff.GOALIE

        return kickoff_position, start_left

    @staticmethod
    def get_dist(data_frame: pd.DataFrame, player: str, frame: int):
        player_df = data_frame[player]
        dist = (player_df['pos_x'][frame]**2 + player_df['pos_y'][frame]**2 + player_df['pos_z'][frame]**2)**(0.5)
        return dist

    @staticmethod
    def get_afk(data_frame: pd.DataFrame, player: str, frame: int, kick_frame: int):
        player_df = data_frame[player]
        return (player_df['pos_x'][frame] == player_df['pos_x'][kick_frame] and
                player_df['pos_y'][frame] == player_df['pos_y'][kick_frame] and
                player_df['pos_z'][frame] == player_df['pos_z'][kick_frame])

    @staticmethod
    def get_touch_position(player: Player, data_frame: pd.DataFrame, k_frame: int, end_frame: int):
        player_df = data_frame[player.name]
        x = abs(player_df['pos_x'][end_frame])
        y = abs(player_df['pos_y'][end_frame])
        if BaseKickoff.get_dist(data_frame, player.name, end_frame) < 700:
            return kickoff.BALL
        if BaseKickoff.get_afk(data_frame, player.name, end_frame, k_frame):
            return kickoff.AFK
        if (x > 2200) and (y > 3600):
            return kickoff.BOOST
        if (x <500) and (y > 3600):
            return kickoff.GOAL
        if (x <500) and (y < 3600):
            return kickoff.CHEAT
        return kickoff.UNKNOWN_TOUCH_POS

    # Todo get what team scored next
    @classmethod
    def get_goal_data(cls, cur_kickoff: KickoffStats, current_goal: Goal, data_frame: pd.DataFrame):
        game_time = data_frame['game', 'time']
        cur_kickoff.touch.kickoff_goal = game_time[current_goal.frame_number] - game_time[cur_kickoff.touch_frame]
