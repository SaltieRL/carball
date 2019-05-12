import inspect
from carball.json_parser import actor


def _get_handlers():
    return list(map(lambda x: x[1], inspect.getmembers(actor, inspect.isclass)))


class FrameParser(object):

    def __init__(self, replay_frames, game):
        self.replay_frames = replay_frames
        self.game = game
        self.replay_version = game.replay_version
        self.frame_data = {
            'frames_data': {},
            'ball_data': {}
        }
        self.all_data = {
            'frames_data': [],
            'ball_data': [],
            'game_info_actor': None
        }
        self.soccar_game_event_actor = None

        self.player_data = {}

        self.parties = {}
        self.player_dicts = {}
        self.team_dicts = {}

        self.player_car_ids = {}  # player_actor_id: car_actor_id
        self.car_player_ids = {}  # car_actor_id: player_actor_id

        self.cameras_data = {}  # player_actor_id: actor_data
        self.demos_data = []  # frame_number: demolish_data

        self.current_car_ids_to_collect = []

        self.actors = {}

    def parse_frames(self):

        type_handler_objects = _get_handlers()

        self.actors = {}
        handlers = {}

        destroyed_actors = set()

        for i, frame in enumerate(self.replay_frames):
            time = frame['time']
            delta = frame['delta']

            self.frame_data['frames_data']['time'] = time
            self.frame_data['frames_data']['delta'] = delta

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
                                          type_handler_objects), None)

                    if handler is not None:
                        handlers[actor_id] = handler.priority, handler(self)

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
                actor = self.actors.get(actor_id, None)
                if actor is not None:
                    handler = handlers.pop(actor_id)
                    handler[1].destroy(actor, time, delta)

            # remove the destroyed actors
            for actor_id in destroyed_actors:
                self.actors.pop(actor_id, None)

            # apply the update handlers
            sorted_handlers = sorted(map(lambda x: (x[0], x[1][0], x[1][1]), handlers.items()), key=lambda x: x[1])
            for handler_tuple in sorted_handlers:
                handler_tuple[2].update(self.actors[handler_tuple[0]], i, time, delta)

            for key, value in self.frame_data.items():
                self.all_data[key].append(value.copy())

            # for actor_id, handler in handlers.items():
            #     actor = self.actors[actor_id]
            #     handler.post_process_frame(actor, time, delta)

            self.current_car_ids_to_collect.clear()

        player_ball_data = {
            'ball': self.all_data['ball_data']
        }

        self.all_data['player_ball_data'] = player_ball_data


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
