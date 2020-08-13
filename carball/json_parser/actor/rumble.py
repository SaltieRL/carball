import re
from .base import *


class RumbleItemHandler(BaseActorHandler):

    @classmethod
    def can_handle(cls, actor: dict) -> bool:
        return actor['TypeName'].startswith('Archetypes.SpecialPickups.SpecialPickup_')

    def update(self, actor: dict, frame_number: int, time: float, delta: float) -> None:
        car_actor_id = actor.get('TAGame.CarComponent_TA:Vehicle', {}).get('actor', None)
        if car_actor_id is not None and car_actor_id in self.parser.current_car_ids_to_collect:
            player_actor_id = self.parser.car_player_ids[car_actor_id]
            item_name = actor['TypeName'] \
                .replace('Archetypes.SpecialPickups.SpecialPickup_', '')
            # CamelCase to snake_case
            item_name = re.sub('([A-Z]+)', r'_\1', item_name).lower()[1:]
            # item is active when this is odd
            item_active = actor.get(COMPONENT_REPLICATED_ACTIVE_KEY, 0) % 2 == 1

            self.parser.player_data[player_actor_id][frame_number]['power_up'] = item_name
            self.parser.player_data[player_actor_id][frame_number]['power_up_active'] = item_active
