from enum import Enum

import pandas as pd
import numpy as np

from ..simulator.map_constants import MAP_Y


class FieldType(Enum):
    STANDARD = 1


STANDARD_FIELD_LENGTH_HALF = 5120
STANDARD_FIELD_WIDTH_HALF = 4096
STANDARD_GOAL_WIDTH_HALF = 893

BALL_SIZE = 92.75
HEIGHT_0_BALL_LIM = 95  # Height of ball when on ground
HEIGHT_0_LIM = 20  # Height of car when on ground
HEIGHT_1_LIM = 840  # Goal height

MAP_THIRD = MAP_Y / 6

NEUTRAL_ZONE = MAP_Y / 20

# Max car speed (boosting) in uu/s
MAX_CAR_SPEED = 2300

class FieldConstants:
    field_type = FieldType.STANDARD

    corner = np.array([STANDARD_FIELD_WIDTH_HALF - STANDARD_GOAL_WIDTH_HALF,
                       STANDARD_FIELD_LENGTH_HALF - STANDARD_GOAL_WIDTH_HALF])
    near_wall = np.array([STANDARD_FIELD_WIDTH_HALF - STANDARD_GOAL_WIDTH_HALF / 2,
                          STANDARD_FIELD_LENGTH_HALF - STANDARD_GOAL_WIDTH_HALF / 2])
    on_wall = np.array([STANDARD_FIELD_WIDTH_HALF, STANDARD_FIELD_LENGTH_HALF]) - 30
    rectangle_lower = np.array(-near_wall)
    rectangle_higher = np.array(near_wall)

    def __init__(self, field_type=FieldType.STANDARD):
        self.field_type = field_type

    """
    All functions here assume the car is on the blue team and the game is played on a standard map.
    return: Boolean series that can be used to index the original data_frame to sum deltas with.
    """

    # The first two values are X,Y. The last value is (RLBot_label +1) and multiplied by 10 if its a bigboost.
    # Bigboosts are *10 so that all big boost values are larger than all small boost values, for easy querying.
    # If nobody needs these to be RLBot labels, this can be simplified.
    def get_big_pads(self, field_type=None):
        if field_type is None:
            field_type = self.field_type
        if field_type == FieldType.STANDARD:
            return np.array([
                (3072, -4096, 50),
                (-3072, -4096, 40),
                (3584, 0, 190),
                (-3584, 0, 160),
                (3072, 4096, 300),
                (-3072, 4096, 310)])
        else:
            raise NotImplementedError

    def get_small_pads(self, field_type=None):
        if field_type is None:
            field_type = self.field_type
        if field_type == FieldType.STANDARD:
            return np.array([
                (0.0, -4240.0, 1),
                (-1792.0, -4184.0, 2),
                (1792.0, -4184.0, 3),
                (- 940.0, -3308.0, 6),
                (940.0, -3308.0, 7),
                (0.0, -2816.0, 8),
                (-3584.0, -2484.0, 9),
                (3584.0, -2484.0, 10),
                (-1788.0, -2300.0, 11),
                (1788.0, -2300.0, 12),
                (-2048.0, -1036.0, 13),
                (0.0, -1024.0, 14),
                (2048.0, -1036.0, 15),
                (-1024.0, 0.0, 17),
                (1024.0, 0.0, 18),
                (-2048.0, 1036.0, 20),
                (0.0, 1024.0, 21),
                (2048.0, 1036.0, 22),
                (-1788.0, 2300.0, 23),
                (1788.0, 2300.0, 24),
                (-3584.0, 2484.0, 25),
                (3584.0, 2484.0, 26),
                (0.0, 2816.0, 27),
                (- 940.0, 3310.0, 28),
                (940.0, 3308.0, 29),
                (-1792.0, 4184.0, 32),
                (1792.0, 4184.0, 33),
                (0.0, 4240.0, 34)])
        else:
            raise NotImplementedError

    def get_neutral_zone(self, player_data_frame, **kwargs):
        return self.abs(player_data_frame.pos_y) < NEUTRAL_ZONE

    def get_half_0(self, player_data_frame, **kwargs):
        return player_data_frame.pos_y < 0

    def get_half_1(self, player_data_frame, **kwargs):
        return player_data_frame.pos_y > 0

    def get_third_0(self, player_data_frame, **kwargs):
        return player_data_frame.pos_y < -MAP_THIRD

    def get_third_1(self, player_data_frame, **kwargs):
        return (-MAP_THIRD < player_data_frame.pos_y) & (player_data_frame.pos_y < MAP_THIRD)

    def get_third_2(self, player_data_frame, **kwargs):
        return player_data_frame.pos_y > MAP_THIRD

    def get_height_0(self, player_data_frame, **kwargs):
        return player_data_frame.pos_z < HEIGHT_0_LIM

    def get_height_0_ball(self, player_data_frame, **kwargs):
        return player_data_frame.pos_z < HEIGHT_0_BALL_LIM

    def get_height_1(self, player_data_frame, **kwargs):
        return (HEIGHT_0_LIM < player_data_frame.pos_z) & (player_data_frame.pos_z < HEIGHT_1_LIM) \
               & (player_data_frame.pos_x.abs() < self.on_wall[0]) & (player_data_frame.pos_y.abs() < self.on_wall[1])

    def get_height_2(self, player_data_frame, **kwargs):
        return (player_data_frame.pos_z > HEIGHT_1_LIM) \
               & (player_data_frame.pos_x.abs() < self.on_wall[0]) & (player_data_frame.pos_y.abs() < self.on_wall[1])

    def get_ball_0(self, player_data_frame, ball_data_frame):
        """Ball is closer to goal 0 than player"""
        return player_data_frame.pos_y < ball_data_frame.pos_y

    def get_ball_1(self, player_data_frame, ball_data_frame):
        """Ball is closer to goal 1 than player"""
        return player_data_frame.pos_y > ball_data_frame.pos_y

    def get_wall_time(self, player_data_frame, **kwargs):
        return ~((self.rectangle_lower[0] <= player_data_frame.pos_x) &
                 (player_data_frame.pos_x <= self.rectangle_higher[0]) &
                 (self.rectangle_lower[1] <= player_data_frame.pos_y) &
                 (player_data_frame.pos_y <= self.rectangle_higher[1]))

    def get_on_wall(self, player_data_frame, **kwargs):
        return (player_data_frame.pos_x.abs() > self.on_wall[0]) | (player_data_frame.pos_y.abs() > self.on_wall[1])

    def get_corner_time(self, player_data_frame, **kwargs):
        return (((player_data_frame.pos_x >= self.corner[0]) |
                 (player_data_frame.pos_x <= -self.corner[0])) &
                ((player_data_frame.pos_y >= self.corner[1]) |
                 (player_data_frame.pos_y <= - self.corner[1])))

    def abs(self, value):
        if value is pd.DataFrame:
            return value.abs()
        else:
            return abs(value)
