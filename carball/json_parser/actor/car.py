import logging
from .base import *
from carball.json_parser.actor_parsing import CarActor

logger = logging.getLogger(__name__)


class CarHandler(BaseActorHandler):
    type_name = 'Archetypes.Car.Car_Default'

    def update(self, actor: dict, frame_number: int, time: float, delta: float) -> None:
        if 'Engine.Pawn:PlayerReplicationInfo' not in actor:
            return

        player_actor_id = actor['Engine.Pawn:PlayerReplicationInfo']['actor']
        if player_actor_id == -1:
            self.add_demo(actor, frame_number)
            return
        # assign car player links
        self.parser.player_car_ids[player_actor_id] = actor['Id']
        self.parser.car_player_ids[actor['Id']] = player_actor_id

        RBState = actor.get(REPLICATED_RB_STATE_KEY, {})
        # bDriving is missing?! TODO: Investigate bDriving in RBState
        # car_is_driving = RBState.get("rigid_body_state", {}).get("TAGame.Vehicle_TA:bDriving", False)
        car_is_sleeping = RBState.get('sleeping', True)
        # only collect data if car is driving and not sleeping
        if not car_is_sleeping:
            self.parser.current_car_ids_to_collect.append(actor['Id'])

            data_dict = CarActor.get_data_dict(actor)
            # save data from here
            self.parser.player_data[player_actor_id][frame_number].update(data_dict)

        # get demo data
        self.add_demo(actor, frame_number)

        if player_actor_id not in self.parser.car_dicts:
            self.parser.car_dicts[player_actor_id] = {'team_paint': {}}

        team_paint = actor['TAGame.Car_TA:TeamPaint']

        self.parser.car_dicts[player_actor_id]['team_paint'][team_paint['team']] = {
            'primary_color': team_paint['primary_color'],
            'accent_color': team_paint['accent_color'],
            'primary_finish': team_paint['primary_finish'],
            'accent_finish': team_paint['accent_finish']
        }

    def add_demo(self, actor, frame_number):
        if 'TAGame.Car_TA:ReplicatedDemolish' in actor:
            demo_data = actor['TAGame.Car_TA:ReplicatedDemolish']
            # add attacker and victim player ids
            attacker_car_id = demo_data['attacker']
            victim_car_id = demo_data['victim']
            if attacker_car_id != -1 and victim_car_id != -1 and attacker_car_id < 1e9 and victim_car_id < 1e9:
                # Filter out weird stuff where it's not a demo
                # frame 1 of 0732D41D4AF83D610AE2A988ACBC977A (rlcs season 4 eu)
                attacker_player_id = self.parser.car_player_ids[attacker_car_id]
                victim_player_id = self.parser.car_player_ids[victim_car_id]
                if attacker_player_id != -1 and victim_player_id != -1:
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
