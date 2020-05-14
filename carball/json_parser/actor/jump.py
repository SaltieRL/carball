from .base import *


class ActiveHandler(BaseActorHandler):

    def __init__(self, parser: object, data_key: str):
        super().__init__(parser)
        self.data_key = data_key

    def update(self, actor: dict, frame_number: int, time: float, delta: float) -> None:
        car_actor_id = actor.get('TAGame.CarComponent_TA:Vehicle', {}).get('actor', None)
        if car_actor_id is not None:
            if car_actor_id in self.parser.current_car_ids_to_collect:
                player_actor_id = self.parser.car_player_ids[car_actor_id]
                jump_is_active = actor.get(
                    COMPONENT_ACTIVE_KEY,
                    actor.get(COMPONENT_REPLICATED_ACTIVE_KEY, False))
                self.parser.player_data[player_actor_id][frame_number][self.data_key] = jump_is_active


class JumpHandler(ActiveHandler):
    type_name = 'Archetypes.CarComponents.CarComponent_Jump'

    def __init__(self, parser: object):
        super().__init__(parser, 'jump_active')


class DoubleJumpHandler(ActiveHandler):
    type_name = 'Archetypes.CarComponents.CarComponent_DoubleJump'

    def __init__(self, parser: object):
        super().__init__(parser, 'double_jump_active')


class DodgeHandler(ActiveHandler):
    type_name = 'Archetypes.CarComponents.CarComponent_Dodge'

    def __init__(self, parser: object):
        super().__init__(parser, 'dodge_active')
