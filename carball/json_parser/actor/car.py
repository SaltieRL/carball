import logging
from .base import *
from carball.json_parser.actor_parsing import CarActor

logger = logging.getLogger(__name__)


class CarHandler(BaseActorHandler):
    type_name = 'Archetypes.Car.Car_Default'
    priority = 600

    def update(self, actor, frame_number, time, delta):
        if 'Engine.Pawn:PlayerReplicationInfo' not in actor:
            return

        player_actor_id = actor['Engine.Pawn:PlayerReplicationInfo']
        # assign car player links
        self.parser.player_car_ids[player_actor_id] = actor['Id']
        self.parser.car_player_ids[actor['Id']] = player_actor_id

        RBState = actor.get(REPLICATED_RB_STATE_KEY, {})
        # bDriving is missing?! TODO: Investigate bDriving in RBState
        # car_is_driving = RBState.get("rigid_body_state", {}).get("TAGame.Vehicle_TA:bDriving", False)
        car_is_sleeping = RBState.get("rigid_body_state", {}).get('sleeping', True)
        # only collect data if car is driving and not sleeping
        if not car_is_sleeping:
            # TODO move to parser
            self.parser.current_car_ids_to_collect.append(actor['Id'])

            data_dict = CarActor.get_data_dict(actor, version=self.parser.replay_version)
            # save data from here
            self.parser.player_data[player_actor_id][frame_number].update(data_dict)

        # get demo data
        if 'TAGame.Car_TA:ReplicatedDemolish' in actor:

            demo_data = actor['TAGame.Car_TA:ReplicatedDemolish']['demolish']
            # add attacker and victim player ids
            attacker_car_id = demo_data['attacker_actor_id']
            victim_car_id = demo_data['victim_actor_id']
            if attacker_car_id != -1 and victim_car_id != -1 and \
                    attacker_car_id < 1e9 and victim_car_id < 1e9:
                # Filter out weird stuff where it's not a demo
                # frame 1 of 0732D41D4AF83D610AE2A988ACBC977A (rlcs season 4 eu)
                attacker_player_id = self.parser.car_player_ids[attacker_car_id]
                victim_player_id = self.parser.car_player_ids[victim_car_id]
                demo_data['attacker_player_id'] = attacker_player_id
                demo_data['victim_player_id'] = victim_player_id
                # add frame_number
                demo_data['frame_number'] = frame_number
                self.parser.demos_data.append(demo_data)
                logger.debug('ReplicatedDemolish: Att: %s, Def: %s' %
                             (attacker_player_id, victim_player_id))
                logger.debug('RepDemo Names: Att: %s. Def: %s' %
                             (self.parser.player_dicts[attacker_player_id]['name'],
                              self.parser.player_dicts[victim_player_id]['name']))
                actor.pop('TAGame.Car_TA:ReplicatedDemolish')
