from typing import Dict

import math

RBSTATE = "TAGame.RBActor_TA:ReplicatedRBState"
rbstate = "rigid_body_state"

BALL_DATA_DICT_PAIRS = {
    'pos_x': (RBSTATE, rbstate, 'location', 'x'),
    'pos_y': (RBSTATE, rbstate, 'location', 'y'),
    'pos_z': (RBSTATE, rbstate, 'location', 'z'),
    'rot_x': (RBSTATE, rbstate, 'rotation', 'x', 'value'),
    'rot_y': (RBSTATE, rbstate, 'rotation', 'y', 'value'),
    'rot_z': (RBSTATE, rbstate, 'rotation', 'z', 'value'),
    'vel_x': (RBSTATE, rbstate, 'linear_velocity', 'x'),
    'vel_y': (RBSTATE, rbstate, 'linear_velocity', 'y'),
    'vel_z': (RBSTATE, rbstate, 'linear_velocity', 'z'),
    'ang_vel_x': (RBSTATE, rbstate, 'angular_velocity', 'x'),
    'ang_vel_y': (RBSTATE, rbstate, 'angular_velocity', 'y'),
    'ang_vel_z': (RBSTATE, rbstate, 'angular_velocity', 'z'),
    'hit_team_no': ("TAGame.Ball_TA:HitTeamNum",),
}


class BallActor:
    @staticmethod
    def get_data_dict(actor_data: Dict, version: int = None) -> Dict:
        # is_sleeping = actor_data.get(RBSTATE, {}).get(rbstate, {}).get('sleeping', True)

        data_dict = {}

        for _key, _value_keys in BALL_DATA_DICT_PAIRS.items():
            _value = actor_data
            for _value_key in _value_keys:
                _value = _value.get(_value_key, None)
                if _value is None:
                    break
            data_dict[_key] = _value

        # TODO: Fix rot_x, y, z: currently {'limit: 65536, 'value': x}.

        if version is not None and version >= 7:
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


# these are parsed such that the max values are as follow:
# pos_x: 3088, pos_y: 5424, pos_z: 1826
# mag(vel) = 23000
# mag(ang_vel) = 5500

CAR_DATA_DICT_PAIRS = {
    'pos_x': (RBSTATE, rbstate, 'location', 'x'),
    'pos_y': (RBSTATE, rbstate, 'location', 'y'),
    'pos_z': (RBSTATE, rbstate, 'location', 'z'),
    'rot_x': (RBSTATE, rbstate, 'rotation', 'x', 'value'),
    'rot_y': (RBSTATE, rbstate, 'rotation', 'y', 'value'),
    'rot_z': (RBSTATE, rbstate, 'rotation', 'z', 'value'),
    'new_rot_x': (RBSTATE, rbstate, 'rotation', 'compressed_word_vector', 'x', 'value'),
    'new_rot_y': (RBSTATE, rbstate, 'rotation', 'compressed_word_vector', 'y', 'value'),
    'new_rot_z': (RBSTATE, rbstate, 'rotation', 'compressed_word_vector', 'z', 'value'),
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
    'throttle': ("TAGame.Vehicle_TA:ReplicatedThrottle",),
    'steer': ("TAGame.Vehicle_TA:ReplicatedSteer",),
    'handbrake': ("TAGame.Vehicle_TA:bReplicatedHandbrake",),
}


class CarActor:
    @staticmethod
    def get_data_dict(actor_data: Dict, version: int = None) -> Dict:
        # is_sleeping = actor_data.get(RBSTATE, {}).get(rbstate, {}).get('sleeping', True)

        data_dict = {}

        for _key, _value_keys in CAR_DATA_DICT_PAIRS.items():
            _value = actor_data
            for _value_key in _value_keys:
                _value = _value.get(_value_key, None)
                if _value is None:
                    break
            data_dict[_key] = _value
        if data_dict['rot_x'] is None:
            data_dict['rot_x'] = data_dict['new_rot_x']
            data_dict['rot_y'] = data_dict['new_rot_y']
            data_dict['rot_z'] = data_dict['new_rot_z']

        if version is not None and version >= 7:
            correction_dict = {'pos_x': 100, 'pos_y': 100, 'pos_z': 100,
                               'vel_x': 10, 'vel_y': 10, 'vel_z': 10,
                               'ang_vel_x': 10, 'ang_vel_y': 10, 'ang_vel_z': 10}
            # /100 pos, /10 vel and ang_vel
            for _item, _divisor in correction_dict.items():
                try:
                    data_dict[_item] /= _divisor
                except TypeError:
                    continue
        if version is not None and version >= 7 and data_dict['quat_w'] is not None:
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
            data_dict['rot_x'] = pitch * 65536.0 / math.pi
            data_dict['rot_y'] = yaw * 65536.0 / math.pi
            data_dict['rot_z'] = roll * 65536.0 / math.pi
        return data_dict
