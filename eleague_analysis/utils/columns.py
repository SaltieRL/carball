from enum import Enum


class PlayerColumn(Enum):
    POS_X = 'pos_x'
    POS_Y = 'pos_y'
    POS_Z = 'pos_z'
    VEL_X = 'vel_x'
    VEL_Y = 'vel_y'
    VEL_Z = 'vel_z'
    ROT_X = 'rot_x'
    ROT_Y = 'rot_y'
    ROT_Z = 'rot_z'
    ANG_VEL_X = 'ang_vel_x'
    ANG_VEL_Y = 'ang_vel_y'
    ANG_VEL_Z = 'ang_vel_z'
    THROTTLE = 'throttle'
    STEER = 'steer'
    HANDBRAKE = 'handbrake'
    BALL_CAM = 'ball_cam'
    DODGE_ACTIVE = 'dodge_active'
    DOUBLE_JUMP_ACTIVE = 'double_jump_active'
    JUMP_ACTIVE = 'jump_active'
    BOOST = 'boost'
    BOOST_ACTIVE = 'boost_active'
    PING = 'ping'
    BOOST_COLLECT = 'boost_collect'


class BallColumn(Enum):
    POS_X = 'pos_x'
    POS_Y = 'pos_y'
    POS_Z = 'pos_z'
    VEL_X = 'vel_x'
    VEL_Y = 'vel_y'
    VEL_Z = 'vel_z'
    ROT_X = 'rot_x'
    ROT_Y = 'rot_y'
    ROT_Z = 'rot_z'
    ANG_VEL_X = 'ang_vel_x'
    ANG_VEL_Y = 'ang_vel_y'
    ANG_VEL_Z = 'ang_vel_z'
    HIT_TEAM_NO = 'hit_team_no'


class GameColumn(Enum):
    TIME = 'time'
    DELTA = 'delta'
    SECONDS_REMAINING = 'seconds_remaining'
    REPLICATED_SECONDS_REMAINING = 'replicated_seconds_remaining'
    IS_OVERTIME = 'is_overtime'
    BALL_HAS_BEEN_HIT = 'ball_has_been_hit'
    GOAL_NUMBER = 'goal_number'
