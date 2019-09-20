import logging
from typing import Tuple, List

import pandas as pd
import numpy as np

from carball.analysis.constants.field_constants import BALL_SIZE
from carball.generated.api import game_pb2
from carball.generated.api.player_pb2 import Player
from carball.generated.api.stats import events_pb2

logger = logging.getLogger(__name__)


# noinspection PyTypeChecker
class CarryData:
    def __init__(self, carry_frames: pd.DataFrame, start_frames: pd.Index, end_frames: pd.Index):
        self.carry_frames = carry_frames
        self.end_frames: List[int] = end_frames.values.tolist()
        self.start_frames: List[int] = start_frames.values.tolist()
        self.flicks = dict()

    def add_flick(self, carry_index: int, is_successful: bool):
        self.flicks[carry_index] = is_successful


class CarryDetection:

    def filter_frames(self, data_frame: pd.DataFrame) -> CarryData:
        valid_frames = data_frame[(data_frame.ball.pos_z > (BALL_SIZE + 5)) & (data_frame.ball.pos_z < 600)]

        return CarryData(valid_frames, *self.creat_start_end_frames(valid_frames))

    def create_carry_events(self, carry_data: CarryData, player: Player, proto_game: game_pb2.Game, data_frame: pd.DataFrame):
        """
        Gets all of the carry events and adds them to the protobuf for each individual player.
        """
        player_carry_data, xy_distance, player_frames = self.player_close_frames(carry_data.carry_frames,
                                                                                 carry_data.carry_frames[player.name])

        if len(player_carry_data.start_frames) == 0:
            # No dribbles no go
            return

        modified_carry_data = self.correct_carries(carry_data, player_carry_data, player, proto_game)

        self.add_carry_events(modified_carry_data, xy_distance, data_frame[player.name], player, proto_game)

    def player_close_frames(self, valid_frames: pd.DataFrame,
                            player_frames: pd.DataFrame) -> Tuple[CarryData, pd.DataFrame, pd.DataFrame]:
        """
        Filters out all frames that are not close enough to the player to be a valid carry.
        Filters out carries that are too short
        """

        null_values = player_frames.pos_x.isnull()
        true_valid_frames = valid_frames
        true_player_frames = player_frames
        if null_values.values.any():
            index = player_frames.index[null_values]
            true_valid_frames = valid_frames.drop(index=index)
            true_player_frames = player_frames.drop(index=index)

        xy_distance = ((true_player_frames.pos_x - true_valid_frames.ball.pos_x) ** 2 +
                       (true_player_frames.pos_y - true_valid_frames.ball.pos_y) ** 2) ** 0.5
        carry_frames = true_valid_frames[(xy_distance < (BALL_SIZE * 1.3)) &
                                         (true_player_frames.pos_z < true_valid_frames.ball.pos_z)]

        player_carry_data = CarryData(true_valid_frames, *self.creat_start_end_frames(carry_frames))
        return player_carry_data, xy_distance, true_player_frames
        # look up hits.
        # any hits by the same player within a continuous set of valid frames should count as carries

    def correct_carries(self, carry_data: CarryData, player_carry_data: CarryData,
                        player: Player, proto_game: game_pb2.Game) -> CarryData:
        """
        This modifies carries to correct for certain situations at a better granularity.
        """

        self.add_hits(carry_data, player_carry_data, player, proto_game.game_stats.hits)

        self.merge_carries(carry_data, player_carry_data)

        self.shorten_carries(player_carry_data, player, proto_game.game_stats.hits)

        # Look for the first carry frame and find all hits before it by the same player

        return player_carry_data

    def add_hits(self, carry_data: CarryData, player_carry_data: CarryData, player: Player, hit_list: List[events_pb2.Hit]):
        """
        Adds in frames to the carry in the beginning for the first hit of the carry.
        """
        hit_index = 0
        previous_end_frame = 0
        valid_frame_index = 0
        for frame_index in range(len(player_carry_data.start_frames)):

            starting_frame = player_carry_data.start_frames[frame_index]
            while (valid_frame_index < len(carry_data.end_frames) and
                   carry_data.end_frames[valid_frame_index] < starting_frame):
                valid_frame_index += 1
            valid_start_frame = carry_data.start_frames[valid_frame_index]

            # Get to the correct index before going backwards
            if hit_index >= len(hit_list):
                continue
            while hit_list[hit_index].frame_number < starting_frame:
                if hit_index == len(hit_list) - 1:
                    break
                hit_index += 1

            last_valid_hit = None
            while (hit_index >= 0 and hit_list[hit_index].player_id.id == player.id.id and
                   hit_list[hit_index].frame_number >= valid_start_frame and
                   hit_list[hit_index].frame_number > previous_end_frame):
                last_valid_hit = hit_list[hit_index]
                hit_index -= 1
            if last_valid_hit is not None:
                hit_index += 1

            if last_valid_hit is not None and last_valid_hit.frame_number < starting_frame:
                player_carry_data.start_frames[frame_index] = last_valid_hit.frame_number
            previous_end_frame = player_carry_data.end_frames[frame_index]

    def shorten_carries(self, player_carry_data: CarryData, player: Player, hit_list: List[events_pb2.Hit]):
        """
        Shortens carries in cases where the carry was ended by a player stealing the ball.
        """
        start_frames = player_carry_data.start_frames
        end_frames = player_carry_data.end_frames

        def valid_hit_number(hit_index, carry_index):
            return hit_list[hit_index].frame_number < end_frames[carry_index] and hit_index < len(hit_list) - 1

        hit_index = 0
        for carry_index in range(len(start_frames)):
            while hit_index < len(hit_list) - 1:
                if hit_list[hit_index].frame_number < start_frames[carry_index]:
                    hit_index += 1
                    continue
                if hit_list[hit_index].frame_number >= end_frames[carry_index]:
                    break

                invalid_hit = None
                last_player_hit = None
                while valid_hit_number(hit_index, carry_index):
                    if hit_list[hit_index].player_id.id != player.id.id:
                        # We need to potentially change how the carry occurred
                        if invalid_hit is None:
                            invalid_hit = hit_list[hit_index]
                        while hit_list[hit_index].player_id.id != player.id.id and valid_hit_number(hit_index,
                                                                                                    carry_index):
                            hit_index += 1
                        if hit_list[hit_index].frame_number >= end_frames[carry_index]:
                            # The player never hits it again, end the carry early.
                            player_carry_data.end_frames[carry_index] = invalid_hit.frame_number
                    else:
                        hit_index += 1
                    if (valid_hit_number(hit_index - 1, carry_index) and
                            hit_list[hit_index - 1].player_id.id == player.id.id):
                        last_player_hit = hit_list[hit_index - 1]
                if last_player_hit is None:
                    logger.error('The player never hit the ball during the "carry"')
                    end_frames[carry_index] = start_frames[carry_index]
                else:
                    most_recent_frame = max(last_player_hit.previous_hit_frame_number, start_frames[carry_index])
                    carry_frames = player_carry_data.carry_frames
                    dodge_data = carry_frames[player.name].dodge_active
                    dodge_data = dodge_data.loc[most_recent_frame:last_player_hit.frame_number]
                    has_flicked = dodge_data.where(dodge_data % 2 == 1).last_valid_index()
                    if has_flicked is not None:
                        ending = min(max(last_player_hit.frame_number + 10, end_frames[carry_index]), has_flicked + 20)
                        is_going_up = carry_frames.ball.pos_z[last_player_hit.frame_number:ending].is_monotonic
                        end_frames[carry_index] = has_flicked
                        if is_going_up:
                            player_carry_data.add_flick(carry_index, True)
                        else:
                            player_carry_data.add_flick(carry_index, False)
                    elif last_player_hit.frame_number > start_frames[carry_index]:
                        end_frames[carry_index] = last_player_hit.frame_number

            if hit_index >= len(hit_list) - 1:
                break

    def merge_carries(self, carry_data: CarryData, player_carry_data: CarryData):
        """
        Merges separated player carries that are still within the greater valid carry set.
        This modifies player_carry_data
        """
        start_frames = player_carry_data.start_frames
        end_frames = player_carry_data.end_frames

        merged_start = []
        merged_end = []

        if len(start_frames) == 0:
            return

        if len(start_frames) == 1:
            # Only one potential carry in the indexes, need to convert to mutable list
            player_carry_data.start_frames = [player_carry_data.start_frames[0]]
            player_carry_data.end_frames = [player_carry_data.end_frames[0]]
            return

        # This is all wrong need to redo merging.

        player_frame_index = 0
        for frame_index in range(len(carry_data.end_frames)):
            end_frame = carry_data.end_frames[frame_index]
            start_frame = carry_data.start_frames[frame_index]
            carry_end = None

            # if we have no more valid play indexes then we can exit
            if player_frame_index >= len(start_frames):
                break

            # if the first dribble is after a global carry already started then just continue
            if start_frames[player_frame_index] > end_frame:
                continue

            #  Increment till the player index is inside a valid start frame
            while player_frame_index < len(start_frames) and start_frames[player_frame_index] < start_frame:
                player_frame_index += 1

            # No more player dribbles
            if player_frame_index >= len(start_frames):
                break

            # if the first dribble is after a global carry already started then just continue
            if start_frames[player_frame_index] > end_frame:
                continue

            carry_start = start_frames[player_frame_index]
            # our start frame should now be inside a valid cary
            entered = False
            while player_frame_index < len(start_frames) and end_frames[player_frame_index] < end_frame:
                player_frame_index += 1
                entered = True

            # our end frame should now be outside a valid cary
            if entered:
                player_frame_index -= 1
            carry_end = end_frames[player_frame_index]

            if carry_end is not None:
                merged_start.append(carry_start)
                merged_end.append(carry_end)

        player_carry_data.start_frames = merged_start
        player_carry_data.end_frames = merged_end

    def creat_start_end_frames(self, carry_frames: pd.DataFrame) -> Tuple[List[int], List[int]]:
        """
        Returns the first and last frame of each potential carry
        """
        carry_frame_index = carry_frames.index
        shifted = carry_frame_index.to_series().shift(fill_value=0)
        neg_shifted = carry_frame_index.to_series().shift(periods=-1, fill_value=0)
        start_frames = carry_frame_index[abs(carry_frame_index - shifted) >= 2]
        end_frames = carry_frame_index[abs(carry_frame_index - neg_shifted) >= 2]
        return start_frames, end_frames

    def add_carry_events(self, carry_data: CarryData,
                         xy_distance: pd.DataFrame, player_frames: pd.DataFrame, player: Player, proto_game):

        start_frames = carry_data.start_frames
        end_frames = carry_data.end_frames
        for i in range(len(carry_data.start_frames)):
            total_time = carry_data.carry_frames.index.slice_locs(start_frames[i], end_frames[i])
            carry_frames = carry_data.carry_frames.iloc[total_time[0]:total_time[1]]
            total_time = carry_frames.game.delta.sum()
            if total_time < 1:
                continue

            ball_carry = proto_game.game_stats.ball_carries.add()
            ball_carry.start_frame_number = start_frames[i]
            ball_carry.end_frame_number = end_frames[i]
            ball_carry.player_id.id = player.id.id
            ball_carry.carry_time = total_time
            ball_carry.has_flick = i in carry_data.flicks and carry_data.flicks[i]
            ball_carry.straight_line_distance = self.get_straight_line_distance(player_frames,
                                                                                start_frames[i], end_frames[i])

            z_distance = carry_frames.ball.pos_z - player_frames.pos_z
            xy_carry = xy_distance[start_frames[i]:end_frames[i]]

            # adding stats for this carry
            carry_stats = ball_carry.carry_stats
            carry_stats.average_xy_distance = xy_carry.mean()
            carry_stats.average_z_distance = z_distance.mean()
            carry_stats.average_ball_z_velocity = carry_frames.ball.vel_z.mean()
            carry_stats.variance_xy_distance = xy_carry.var()
            carry_stats.variance_z_distance = z_distance.var()
            carry_stats.variance_ball_z_velocity = carry_frames.ball.vel_z.var()
            carry_stats.average_carry_speed = ((player_frames.vel_x ** 2 + player_frames.vel_y ** 2) ** 0.5).mean()
            carry_stats.distance_along_path = self.get_distance_along_path(player_frames,
                                                                           start_frames[i], end_frames[i])

    def get_distance_along_path(self, player_frames: pd.DataFrame, start_frame: int, end_frame: int):
        pos_x = player_frames.pos_x.loc[start_frame:end_frame].diff()
        pos_y = player_frames.pos_y.loc[start_frame:end_frame].diff()
        return ((pos_x ** 2 + pos_y ** 2) ** 0.5).sum()

    def get_straight_line_distance(self, player_frames: pd.DataFrame, start: int, end: int) -> pd.DataFrame:
        x1 = player_frames.pos_x[start]
        y1 = player_frames.pos_y[start]

        x2 = player_frames.pos_x[end]
        y2 = player_frames.pos_y[end]

        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
