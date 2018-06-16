RBSTATE = "TAGame.RBActor_TA:ReplicatedRBState"

BALL_DATA_DICT_PAIRS = {
    'pos_x': (RBSTATE, 'Position', 'X'),
    'pos_y': (RBSTATE, 'Position', 'Y'),
    'pos_z': (RBSTATE, 'Position', 'Z'),
    'rot_x': (RBSTATE, 'Rotation', 'X'),
    'rot_y': (RBSTATE, 'Rotation', 'Y'),
    'rot_z': (RBSTATE, 'Rotation', 'Z'),
    'vel_x': (RBSTATE, 'LinearVelocity', 'X'),
    'vel_y': (RBSTATE, 'LinearVelocity', 'Y'),
    'vel_z': (RBSTATE, 'LinearVelocity', 'Z'),
    'ang_vel_x': (RBSTATE, 'AngularVelocity', 'X'),
    'ang_vel_y': (RBSTATE, 'AngularVelocity', 'Y'),
    'ang_vel_z': (RBSTATE, 'AngularVelocity', 'Z'),
    'hit_team_no': ("TAGame.Ball_TA:HitTeamNum",),
}


class BallActor:
    @staticmethod
    def get_data_dict(actor_data, version=None):
        RBState = actor_data.get(
            "TAGame.RBActor_TA:ReplicatedRBState", {})
        ball_is_sleeping = RBState.get('Sleeping', True)

        data_dict = {}

        for _key, _value_keys in BALL_DATA_DICT_PAIRS.items():
            _value = actor_data
            for _value_key in _value_keys:
                _value = _value.get(_value_key, None)
                if _value is None:
                    break
            data_dict[_key] = _value

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


CAR_DATA_DICT_PAIRS = {
    'pos_x': (RBSTATE, 'Position', 'X'),
    'pos_y': (RBSTATE, 'Position', 'Y'),
    'pos_z': (RBSTATE, 'Position', 'Z'),
    'rot_x': (RBSTATE, 'Rotation', 'X'),
    'rot_y': (RBSTATE, 'Rotation', 'Y'),
    'rot_z': (RBSTATE, 'Rotation', 'Z'),
    'vel_x': (RBSTATE, 'LinearVelocity', 'X'),
    'vel_y': (RBSTATE, 'LinearVelocity', 'Y'),
    'vel_z': (RBSTATE, 'LinearVelocity', 'Z'),
    'ang_vel_x': (RBSTATE, 'AngularVelocity', 'X'),
    'ang_vel_y': (RBSTATE, 'AngularVelocity', 'Y'),
    'ang_vel_z': (RBSTATE, 'AngularVelocity', 'Z'),
    'throttle': ("TAGame.Vehicle_TA:ReplicatedThrottle",),
    'steer': ("TAGame.Vehicle_TA:ReplicatedSteer",),
    'handbrake': ("TAGame.Vehicle_TA:bReplicatedHandbrake",),
}


class CarActor:
    @staticmethod
    def get_data_dict(actor_data, version=None):
        RBState = actor_data.get(
            "TAGame.RBActor_TA:ReplicatedRBState", {})
        ball_is_sleeping = RBState.get('Sleeping', True)

        data_dict = {}

        for _key, _value_keys in CAR_DATA_DICT_PAIRS.items():
            _value = actor_data
            for _value_key in _value_keys:
                _value = _value.get(_value_key, None)
                if _value is None:
                    break
            data_dict[_key] = _value

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
