from .actor import *

REPLICATED_RB_STATE_KEY = 'TAGame.RBActor_TA:ReplicatedRBState'

_HANDLERS = [
    GameInfoHandler,
    GameEventHandler,
    BallHandler,
    PlayerHandler,
    TeamHandler,
    CarHandler,
    JumpHandler,
    DodgeHandler,
    DoubleJumpHandler,
    BoostHandler,
    BoostPickupHandler,
    CameraSettingsHandler,
    RumbleItemHandler
]

# These handlers will also handle frames with a delta of 0 to match the old implementation
# TODO check if this is needed
_0_DELTA_HANDLERS = [
    GameInfoHandler,
    PlayerHandler
]


def parse_frames(game):
    """
    :return: all_data = {
        'player_ball_data': player_ball_data,
        'player_dicts': player_dicts,
        'team_dicts': team_dicts,
        'frames_data': frames_data,
        'cameras_data': cameras_data
        'demos_data': demos_data
    }

    player_ball_data format:
    {
    'ball': {frame_number: {pos_x, pos_y ...}, f_no2: {...} ...,}
    player_actor_id: {
        frame_number: {
            pos_x, pos_y ...,
            throttle, steer, ...,
            ping, ball_cam
        },
        f_no2: {...} ...,
    }

    currently implemented:
        inputs: posx, posy, posz, rotx, roty, rotz, vx, vy, vz, angvx, angy, angvz, boost_amt
        outputs: throttle, steer, handbrake, boost, jump, doublejump, dodge

    player_dicts  = {player_actor_id : {actor_data}, player_actor_id_2: {actor_data_2}}
    team_dicts = {team_actor_id: {actor_data, 'colour':'blue'/'orange', also includes name}
    frames_data = {frame_number: {time, delta, seconds_remaining, is_overtime, ball_has_been_hit}
    cameras_data = {player_actor_id: actor_data}
    demos_data = {frame_number: demolish_data}

    """
    parser = FrameParser(game.replay_data, game)
    parser.parse_frames()

    player_ball_data = parser.player_data
    player_ball_data['ball'] = parser.ball_data

    return {
        'player_ball_data': player_ball_data,
        'player_dicts': parser.player_dicts,
        'team_dicts': parser.team_dicts,
        'frames_data': parser.frames_data,
        'cameras_data': parser.cameras_data,
        'demos_data': parser.demos_data,
        'game_info_actor': parser.game_info_actor,
        'soccar_game_event_actor': parser.soccar_game_event_actor,
        'parties': parser.parties
    }


class FrameParser(object):

    def __init__(self, replay_frames, game):
        self.replay_frames = replay_frames
        self.game = game
        self.replay_version = game.replay_version

        self.game_info_actor = None
        self.soccar_game_event_actor = None

        self.frames_data = {}
        self.ball_data = {}
        self.player_data = {}

        # dictionaries to contain data in frames
        self.parties = {}
        self.player_dicts = {}
        self.team_dicts = {}

        self.player_car_ids = {}  # player_actor_id: car_actor_id
        self.car_player_ids = {}  # car_actor_id: player_actor_id

        self.cameras_data = {}  # player_actor_id: actor_data
        self.demos_data = []  # frame_number: demolish_data

        # stores car_actor_ids to collect data for at each frame
        self.current_car_ids_to_collect = []

        self.actors = {}

    def parse_frames(self):

        self.actors = {}
        handlers = {}

        destroyed_actors = set()

        current_goal_number = 0

        for i, frame in enumerate(self.replay_frames):
            time = frame['time']
            delta = frame['delta']

            destroyed_actors.clear()

            for replication in frame['replications']:
                actor_id = replication['actor_id']['value']
                actor_status = next(iter(replication['value'].keys()))

                if actor_status == 'spawned':
                    self.actors[actor_id] = {
                        'Id': actor_id,
                        'TypeName': replication['value']['spawned']['object_name'],
                        'ClassName': replication['value']['spawned']['class_name'],
                        'Name': replication['value']['spawned'].get('name', None),
                    }

                    handler = next(filter(lambda handler_cls: handler_cls.can_handle(self.actors[actor_id]),
                                          _HANDLERS), None)

                    if handler is not None:
                        handlers[actor_id] = handler.priority, handler(self), handler in _0_DELTA_HANDLERS

                elif actor_status == 'updated':
                    if actor_id not in self.actors:
                        continue

                    actor = self.actors[actor_id]
                    # update properties
                    for prop in replication['value']['updated']:
                        actor[prop['name']] = find_actual_value(prop['value'])

                elif actor_status == 'destroyed':
                    if actor_id in handlers:
                        destroyed_actors.add(actor_id)

            # apply destroy handlers
            for actor_id in destroyed_actors:
                handlers.pop(actor_id, None)
                self.player_car_ids.pop(actor_id, None)
                self.car_player_ids.pop(actor_id, None)
                self.actors.pop(actor_id, None)

            # stop data collection after goal
            try:
                if i > self.game.goals[current_goal_number].frame_number:
                    # set all players to sleeping after goal
                    for car_actor_id in self.car_player_ids:
                        try:
                            car = self.actors[car_actor_id]
                            car[REPLICATED_RB_STATE_KEY]['Sleeping'] = True
                        except KeyError as e:
                            # Ignore the case where the car does not have a REPLICATED_RB_STATE_KEY
                            pass
                    current_goal_number += 1
            except IndexError:
                # after last goal.
                pass

            # apply the update handlers
            sorted_handlers = sorted(map(lambda x: (x[0],) + x[1], handlers.items()), key=lambda x: x[1])
            for handler_tuple in sorted_handlers:
                handler = handler_tuple[2]

                # skip 0 delta frames, except for these two handlers (matches old implementation)
                if handler_tuple[3] or delta != 0:
                    handler_tuple[2].update(self.actors[handler_tuple[0]], i, time, delta)

            self.current_car_ids_to_collect.clear()


def find_actual_value(value_dict: dict) -> dict or int or bool or str:
    types = ['int', 'boolean', 'string', 'byte', 'str', 'name', ('flagged_int', 'int')]
    if value_dict is None:
        return None
    if 'value' in value_dict:
        value_dict = value_dict['value']
    for _type in types:
        if isinstance(_type, str):
            if _type in value_dict:
                return value_dict[_type]
        else:
            value = value_dict
            if _type[0] in value:
                for type_str in _type:
                    value = value[type_str]
                return value
    else:
        return value_dict
