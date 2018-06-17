RBSTATE = "TAGame.RBActor_TA:ReplicatedRBState"
rbstate = "rigid_body_state"

BALL_DATA_DICT_PAIRS = {
    'pos_x': (RBSTATE, rbstate, 'location', 'x'),
    'pos_y': (RBSTATE, rbstate, 'location', 'y'),
    'pos_z': (RBSTATE, rbstate, 'location', 'z'),
    'rot_x': (RBSTATE, rbstate, 'rotation', 'x'),
    'rot_y': (RBSTATE, rbstate, 'rotation', 'y'),
    'rot_z': (RBSTATE, rbstate, 'rotation', 'z'),
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
    def get_data_dict(actor_data, version=None):
        RBState = actor_data.get(
            "TAGame.RBActor_TA:ReplicatedRBState", {})
        ball_is_sleeping = RBState.get('sleeping', True)
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
