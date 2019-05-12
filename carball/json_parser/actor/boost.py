from .base import *

BOOST_PER_SECOND = 80 * 1 / .93  # boost used per second out of 255
REPLICATED_PICKUP_KEY = 'TAGame.VehiclePickup_TA:ReplicatedPickupData'


class BoostHandler(BaseActorHandler):
    type_name = 'Archetypes.CarComponents.CarComponent_Boost'

    def update(self, actor: dict, frame_number: int, time: float, delta: float) -> None:
        car_actor_id = actor.get('TAGame.CarComponent_TA:Vehicle', None)

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
        if REPLICATED_PICKUP_KEY in actor and \
                actor[REPLICATED_PICKUP_KEY] != -1 and \
                'instigator_id' in actor[REPLICATED_PICKUP_KEY]['pickup']:
            car_actor_id = actor[REPLICATED_PICKUP_KEY]['pickup']['instigator_id']
            if car_actor_id in self.parser.car_player_ids:
                player_actor_id = self.parser.car_player_ids[car_actor_id]
                if frame_number in self.parser.player_data[player_actor_id]:
                    self.parser.player_data[player_actor_id][frame_number]['boost_collect'] = True
                    # TODO: Investigate and fix random imaginary boost collects
                # set to false after acknowledging it's turned True
                # it does not turn back false immediately although boost is only collected once.
                # using actor_id!=-1
                actor[REPLICATED_PICKUP_KEY]['pickup']["instigator_id"] = -1
