import math
from typing import Dict

RBSTATE = "TAGame.RBActor_TA:ReplicatedRBState"
rbstate = "rigid_body_state"

RB_STATE_DICT_PAIRS = {
    'pos_x': (RBSTATE, rbstate, 'location', 'x'),
    'pos_y': (RBSTATE, rbstate, 'location', 'y'),
    'pos_z': (RBSTATE, rbstate, 'location', 'z'),
    'rot_x': (RBSTATE, rbstate, 'rotation', 'compressed_word_vector', 'x', 'value'),
    'rot_y': (RBSTATE, rbstate, 'rotation', 'compressed_word_vector', 'y', 'value'),
    'rot_z': (RBSTATE, rbstate, 'rotation', 'compressed_word_vector', 'z', 'value'),
    'quat_w': (RBSTATE, rbstate, 'rotation', 'quaternion', 'w'),
    'quat_x': (RBSTATE, rbstate, 'rotation', 'quaternion', 'x'),
    'quat_y': (RBSTATE, rbstate, 'rotation', 'quaternion', 'y'),
    'quat_z': (RBSTATE, rbstate, 'rotation', 'quaternion', 'z'),
    'vel_x': (RBSTATE, rbstate, 'linear_velocity', 'x'),
    'vel_y': (RBSTATE, rbstate, 'linear_velocity', 'y'),
    'vel_z': (RBSTATE, rbstate, 'linear_velocity', 'z'),
    'ang_vel_x': (RBSTATE, rbstate, 'angular_velocity', 'x'),
    'ang_vel_y': (RBSTATE, rbstate, 'angular_velocity', 'y'),
    'ang_vel_z': (RBSTATE, rbstate, 'angular_velocity', 'z'),
}

BALL_DATA_DICT_PAIRS = {
    **RB_STATE_DICT_PAIRS,
    'hit_team_no': ("TAGame.Ball_TA:HitTeamNum",),
}


class BallActor:
    @staticmethod
    def get_data_dict(actor_data: Dict, version: int = None) -> Dict:
        # is_sleeping = actor_data.get(RBSTATE, {}).get(rbstate, {}).get('sleeping', True)
        data_dict = get_data_dict_from_pairs(actor_data, pairs=BALL_DATA_DICT_PAIRS)
        data_dict = standardise_data_dict(data_dict, version)
        return data_dict


# these are parsed such that the max values are as follow:
# pos_x: 3088, pos_y: 5424, pos_z: 1826
# mag(vel) = 23000
# mag(ang_vel) = 5500

CAR_DATA_DICT_PAIRS = {
    **RB_STATE_DICT_PAIRS,
    'throttle': ("TAGame.Vehicle_TA:ReplicatedThrottle",),
    'steer': ("TAGame.Vehicle_TA:ReplicatedSteer",),
    'handbrake': ("TAGame.Vehicle_TA:bReplicatedHandbrake",),
}


class CarActor:
    @staticmethod
    def get_data_dict(actor_data: Dict, version: int = None) -> Dict:
        # is_sleeping = actor_data.get(RBSTATE, {}).get(rbstate, {}).get('sleeping', True)
        data_dict = get_data_dict_from_pairs(actor_data, pairs=CAR_DATA_DICT_PAIRS)
        data_dict = standardise_data_dict(data_dict, version)
        return data_dict


def get_data_dict_from_pairs(actor_data: dict, pairs: dict) -> dict:
    data_dict = {}

    for _key, _value_keys in pairs.items():
        _value = actor_data
        for _value_key in _value_keys:
            _value = _value.get(_value_key, None)
            if _value is None:
                break
        data_dict[_key] = _value
    return data_dict


def standardise_data_dict(data_dict: dict, version: int = None) -> dict:
    if version is not None and version >= 7:
        data_dict = rescale_to_uu(data_dict)
    if data_dict['quat_w'] is None:
        data_dict = convert_to_radians(data_dict)
    if version is not None and version >= 7 and data_dict['quat_w'] is not None:
        data_dict = convert_quat_to_rot(data_dict)
    data_dict.pop('quat_w')
    data_dict.pop('quat_x')
    data_dict.pop('quat_y')
    data_dict.pop('quat_z')
    return data_dict


def rescale_to_uu(data_dict: dict) -> dict:
    # handle psyonix's rounding to 2dp (and storing 1.00 as 100)
    correction_dict = {'pos_x': 100, 'pos_y': 100, 'pos_z': 100,
                       'vel_x': 10, 'vel_y': 10, 'vel_z': 10,
                       'ang_vel_x': 10, 'ang_vel_y': 10, 'ang_vel_z': 10}
    # /100 pos, /10 vel and ang_vel
    for _item, _divisor in correction_dict.items():
        try:
            data_dict[_item] /= _divisor
        except TypeError:
            continue
    return data_dict


def convert_to_radians(data_dict: dict) -> dict:
    # converts from int16 to radians
    try:
        data_dict['rot_x'] *= -2 * math.pi / 65535
        data_dict['rot_y'] = (data_dict['rot_y'] / 65535 - 0.5) * 2 * math.pi
        data_dict['rot_z'] *= -2 * math.pi / 65535
    except TypeError:
        pass
    return data_dict


def convert_quat_to_rot(data_dict: dict) -> dict:
    # https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles#Quaternion_to_Euler_Angles_Conversion

    w = data_dict['quat_w']
    x = data_dict['quat_x']
    y = data_dict['quat_y']
    z = data_dict['quat_z']

    sinr = 2.0 * (w * x + y * z)
    cosr = 1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(sinr, cosr)

    sinp = 2.0 * (w * y - z * x)
    if abs(sinp) >= 1:
        pitch = math.copysign(math.pi / 2, sinp)
    else:
        pitch = math.asin(sinp)

    siny = 2.0 * (w * z + x * y)
    cosy = 1.0 - 2.0 * (y * y + z * z)
    yaw = math.atan2(siny, cosy)
    data_dict['rot_x'] = pitch
    data_dict['rot_y'] = yaw
    data_dict['rot_z'] = roll

    return data_dict
