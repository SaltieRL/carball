import logging
from typing import Tuple, List

import pandas as pd

from carball.analysis.constants.field_constants import BALL_SIZE
from carball.generated.api import game_pb2
from carball.generated.api.player_pb2 import Player

logger = logging.getLogger(__name__)

class CarryData:
    def __init__(self, carry_frames: pd.DataFrame, start_frames: List[int], end_frames: List[int]):
        self.carry_frames = carry_frames
        self.end_frames = end_frames
        self.start_frames = start_frames


class CarryDetection:

    def filter_frames(self, data_frame: pd.DataFrame) -> CarryData:
        valid_frames = data_frame[(data_frame.ball.pos_z > (BALL_SIZE + 5)) & (data_frame.ball.pos_z < 500)]
        return CarryData(valid_frames, *self.creat_start_end_frames(valid_frames))

    def create_carry_events(self, carry_data: CarryData, player: Player, proto_game: game_pb2.Game):
        """
        Gets all of the carry events and adds them to the protobuf for each individual player.
        """
        player_carry_data, xy_distance, player_frames = self.player_close_frames(carry_data.carry_frames,
                                                                            carry_data.carry_frames[player.name])

        modified_carry_data = self.correct_carries(carry_data, player_carry_data, player, proto_game)

        self.add_carry_events(modified_carry_data, xy_distance, player_frames, player, proto_game)

    def player_close_frames(self, valid_frames: pd.DataFrame,
                            player_frames: pd.DataFrame) -> Tuple[CarryData, pd.DataFrame, pd.DataFrame]:
        """
        Filters out all frames that are not close enough to the player to be a valid carry.
        Filters out dribbles that are too short
        """

        xy_distance = ((player_frames.pos_x - valid_frames.ball.pos_x) ** 2 +
                       (player_frames.pos_y - valid_frames.ball.pos_y) ** 2) ** 0.5
        carry_frames = valid_frames[(xy_distance < BALL_SIZE) & (player_frames.pos_z < valid_frames.ball.pos_z)]

        player_carry_data = CarryData(valid_frames, *self.creat_start_end_frames(carry_frames))
        return player_carry_data, xy_distance, player_frames
        # look up hits.
        # any hits by the same player within a continous set of valid frames should count as carrys

    def merge_dribbles(self, carry_data: CarryData, player_carry_data: CarryData):
        """
        Merges separated dribbles that are still within the valid dribble set.
        """
        start_frames = player_carry_data.start_frames
        end_frames = player_carry_data.end_frames

        merged_start = []
        merged_end = []

        previous_start = -1
        previous_end = 1

        for frame_index in range(len(start_frames) - 1):
            total_frame_number = frame_index
            while total_frame_number < len(carry_data.start_frames) and carry_data.start_frames[total_frame_number] < start_frames[frame_index]:
                total_frame_number += 1
            if total_frame_number == len(carry_data.start_frames):
                logger.warning("can not merge frames anymore.")
                break

            end_frame = end_frames[frame_index]
            next_start = start_frames[frame_index + 1]
            if (end_frame < carry_data.start_frames[total_frame_number] < next_start or
                    end_frame < carry_data.end_frames[total_frame_number] < next_start):
                if previous_start != -1:
                    merged_start.append(previous_start)
                    merged_end.append(previous_end)
                    previous_start = -1
                else:
                    merged_start.append(start_frames[frame_index])
                    merged_end.append(end_frames[frame_index])
            else:
                if previous_start == -1:
                    previous_start = start_frames[frame_index]
                previous_end = end_frames[frame_index + 1]

        if previous_start != -1:
            merged_start.append(previous_start)
            merged_end.append(previous_end)
        player_carry_data.start_frames = merged_start
        player_carry_data.end_frames = merged_end

    def correct_carries(self, carry_data: CarryData, player_carry_data: CarryData,
                        player: Player, proto_game: game_pb2.Game) -> CarryData:
        """
        This modifies carries to correct for certain situations at a better granularity.
        For examples cases where one dribble was instead counted as 2.
        cases where the dribble should stop counting.
        """

        self.merge_dribbles(carry_data, player_carry_data)
        start_frames = player_carry_data.start_frames
        end_frames = player_carry_data.end_frames

        starting_hit_index = 0
        hit_list = proto_game.game_stats.hits

        # to expand you look at all hits before the start frame and check if they are valid for this purpose.


        # Need to start cutting off dribbles if someone other than the player hits the ball and the player does not gain another hit on the ball before the dribble ends.

        for frame_index in range(len(start_frames)):
            hit_number = 0
            for i in range(hit_number, len(hit_list)):
                if hit_list[i].frame_number < start_frames[frame_index]:
                    continue
                if hit_list[i].frame_number > end_frames[frame_index]:
                    break

                while hit_list[hit_number].frame_number < end_frames[frame_index]:
                    if hit_list[hit_number].player_id.id != player.id.id:
                        # We have an imposter dribble!
                    hit_number += 1


            if starting_hit_index >= len(hit_list) - 1:
                logger.warning("We have reached a point where dribbles should not exist anymore")
                break
        # Look for the first carry frame and find all hits before it by the same player


        return player_carry_data

    def get_distance(self, player_frames: pd.DataFrame, start: int, end: int) -> pd.DataFrame:
        x1 = player_frames.pos_x[start]
        y1 = player_frames.pos_y[start]

        x2 = player_frames.pos_x[end]
        y2 = player_frames.pos_y[end]

        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

    def creat_start_end_frames(self, carry_frames: pd.DataFrame) -> Tuple[List[int], List[int]]:
        carry_frame_index = carry_frames.index
        shifted = carry_frame_index.to_series().shift(fill_value=0)
        neg_shifted = carry_frame_index.to_series().shift(periods=-1, fill_value=0)
        start_frames = carry_frame_index[abs(carry_frame_index - shifted) > 3]
        end_frames = carry_frame_index[abs(carry_frame_index - neg_shifted) > 3]
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
            ball_carry.distance_traveled = self.get_distance(player_frames, start_frames[i], end_frames[i])

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
