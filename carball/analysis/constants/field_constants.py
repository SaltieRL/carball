from enum import Enum

import pandas as pd

from ..simulator.map_constants import MAP_Y


class FieldType(Enum):
    STANDARD = 1


HEIGHT_0_LIM = 20  # Height of car when on ground
HEIGHT_1_LIM = 840  # Goal height

MAP_THIRD = MAP_Y / 6

NEUTRAL_ZONE = MAP_Y / 20


class FieldConstants:

    field_type = FieldType.STANDARD

    def __init__(self, field_type=FieldType.STANDARD):
        self.field_type = field_type

    """
    All functions here assume the car is on the blue team and the game is played on a standard map.
    return: Boolean series that can be used to index the original data_frame to sum deltas with.
    """

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

    def get_height_1(self, player_data_frame, **kwargs):
        return (HEIGHT_0_LIM < player_data_frame.pos_z) & (player_data_frame.pos_z < HEIGHT_1_LIM)

    def get_height_2(self, player_data_frame, **kwargs):
        return player_data_frame.pos_z > HEIGHT_1_LIM

    def get_ball_0(self, player_data_frame, ball_data_frame):
        """Ball is closer to goal 0 than player"""
        return player_data_frame.pos_y < ball_data_frame.pos_y

    def get_ball_1(self, player_data_frame, ball_data_frame):
        """Ball is closer to goal 1 than player"""
        return player_data_frame.pos_y > ball_data_frame.pos_y

    def abs(self, value):
        if value is pd.DataFrame:
            return value.abs()
        else:
            return abs(value)
