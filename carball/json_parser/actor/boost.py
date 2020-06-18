from .base import *

BOOST_PER_SECOND = 80 * 1 / .93  # boost used per second out of 255
REPLICATED_PICKUP_KEY = 'TAGame.VehiclePickup_TA:ReplicatedPickupData'
REPLICATED_PICKUP_KEY_168 = 'TAGame.VehiclePickup_TA:NewReplicatedPickupData'


def get_boost_actor_data(actor: dict):
    if REPLICATED_PICKUP_KEY in actor:
        actor = actor[REPLICATED_PICKUP_KEY]
        if actor is not None and actor != -1:
            actor = actor['pickup']
            if actor is not None and 'instigator_id' in actor and actor["instigator_id"] != -1:
                return actor
    elif REPLICATED_PICKUP_KEY_168 in actor:
        actor = actor[REPLICATED_PICKUP_KEY_168]
        if actor is not None and actor != -1:
            actor = actor['pickup_new']
            if actor is not None and 'instigator_id' in actor and actor["instigator_id"] != -1:
                return actor
    return None


class BoostHandler(BaseActorHandler):
    type_name = 'Archetypes.CarComponents.CarComponent_Boost'

    def update(self, actor: dict, frame_number: int, time: float, delta: float) -> None:
        car_actor_id = actor.get('TAGame.CarComponent_TA:Vehicle', {}).get('actor', None)

        if car_actor_id is None or car_actor_id not in self.parser.current_car_ids_to_collect:
            return

        player_actor_id = self.parser.car_player_ids[car_actor_id]
        boost_is_active_random_int = actor.get(
            COMPONENT_ACTIVE_KEY,
            actor.get(COMPONENT_REPLICATED_ACTIVE_KEY, False))
        # boost_is_active when random_int is odd?!
        boost_is_active = (boost_is_active_random_int % 2 == 1)
        if boost_is_active:
            # manually decrease car boost amount (not shown in replay)
            # i assume game calculates the decrease itself similarly
            boost_amount = max(0, actor.get('TAGame.CarComponent_Boost_TA:ReplicatedBoostAmount',
                                            0) - delta * BOOST_PER_SECOND)
            actor['TAGame.CarComponent_Boost_TA:ReplicatedBoostAmount'] = boost_amount
        else:
            boost_amount = actor.get('TAGame.CarComponent_Boost_TA:ReplicatedBoostAmount', None)

        self.parser.player_data[player_actor_id][frame_number]['boost'] = boost_amount
        self.parser.player_data[player_actor_id][frame_number]['boost_active'] = boost_is_active


class BoostPickupHandler(BaseActorHandler):

    @classmethod
    def can_handle(cls, actor: dict) -> bool:
        return actor['ClassName'] == 'TAGame.VehiclePickup_Boost_TA'

    def update(self, actor: dict, frame_number: int, time: float, delta: float) -> None:
        boost_actor = get_boost_actor_data(actor)
        if boost_actor is not None:
            car_actor_id = boost_actor['instigator_id']
            if car_actor_id in self.parser.car_player_ids:
                player_actor_id = self.parser.car_player_ids[car_actor_id]
                if frame_number in self.parser.player_data[player_actor_id]:
                    actor = self.parser.player_data[player_actor_id]
                    frame_number_look_back = frame_number - 1
                    previous_boost_data = None
                    while frame_number_look_back >= 0:
                        try:
                            previous_boost_data = actor[frame_number_look_back]['boost']
                        except KeyError:
                            previous_boost_data = None
                        if previous_boost_data is not None:
                            break
                        frame_number_look_back -= 1
                    try:
                        current_boost_data = actor[frame_number]['boost']
                    except KeyError:
                        current_boost_data = None

                    # Ignore any phantom boosts
                    if (previous_boost_data is not None and current_boost_data is not None and
                            (255 > previous_boost_data < current_boost_data)):
                        actor[frame_number]['boost_collect'] = True
                        # set to false after acknowledging it's turned True
                        # it does not turn back false immediately although boost is only collected once.
                        # using actor_id!=-1
                        boost_actor["instigator_id"] = -1
