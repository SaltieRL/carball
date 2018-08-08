from typing import Dict

import numpy as np

from .saltie_game import SaltieGame
from ..hit_detection.base_hit import BaseHit
from ..simulator.ball_simulator import BallSimulator
from ..simulator.map_constants import *


class SaltieHit:

    def __init__(self, hit: BaseHit,
                 pass_: bool = False, passed: bool = False,
                 dribble: bool = False, dribble_continuation: bool = False,
                 shot: bool = False, goal: bool = False,
                 assist: bool = False, assisted: bool = False,
                 save: bool = False,
                 distance: float = None,
                 ):
        self.hit = hit
        self.pass_ = pass_
        self.passed = passed
        self.dribble = dribble
        self.dribble_continuation = dribble_continuation
        self.shot = shot
        self.goal = goal
        self.assist = assist
        self.assisted = assisted
        self.save = save
        self.distance = distance

        self.distance_to_goal = self.get_distance_to_goal()

        self.previous_hit: 'SaltieHit' = None
        self.next_hit: 'SaltieHit' = None

    def get_distance_to_goal(self):
        _goal_x = min(max(self.hit.ball_data['pos_x'], GOAL_X / 2), -GOAL_X / 2)
        _goal_y = -MAP_Y / 2 if self.hit.player.is_orange else MAP_Y / 2

        displacement = self.hit.ball_data[['pos_x', 'pos_y']].values - (_goal_x, _goal_y)
        distance = np.sqrt(np.square(displacement).sum())

        return distance

    @staticmethod
    def get_saltie_hits_from_game(saltie_game: SaltieGame):
        hit_analytics_dict: Dict[int, SaltieHit] = {}
        for hit in saltie_game.hits.values():
            saltie_hit = SaltieHit(hit)
            hit_analytics_dict[saltie_hit.hit.frame_number] = saltie_hit

        hit_frame_numbers = sorted(hit_analytics_dict)

        # find last hit by goalscorer for each goal frame
        for goal_number, goal in enumerate(saltie_game.api_game.goals):
            goal_kickoff_frame = saltie_game.kickoff_frames[goal_number]
            last_goalscorer_saltie_hit = None
            for hit_frame_number in hit_frame_numbers:
                saltie_hit = hit_analytics_dict[hit_frame_number]
                if not goal_kickoff_frame <= saltie_hit.hit.frame_number <= goal.frame_number:
                    continue
                if saltie_hit.hit.player is goal.player:
                    last_goalscorer_saltie_hit = saltie_hit

            if last_goalscorer_saltie_hit is None:
                print("Could not find hit for goal: %s" % goal)
            else:
                last_goalscorer_saltie_hit.goal = True
                # print("Found hit for goal: %s, %s" % (goal.frame_number, goal.hit))
                # print("Player: %s scored %s goals" % (goal.player.name, goal.player.goals))

        # find passes and assists
        for hit_number in range(len(hit_frame_numbers)):
            hit_frame_number = hit_frame_numbers[hit_number]
            saltie_hit = hit_analytics_dict[hit_frame_number]

            saltie_hit_goal_number = get_goal_number(hit_frame_number, saltie_game)
            # previous hit
            previous_saltie_hit = None
            try:
                previous_hit_frame_number = hit_frame_numbers[hit_number - 1]
                if get_goal_number(previous_hit_frame_number, saltie_game) == saltie_hit_goal_number:
                    previous_saltie_hit = hit_analytics_dict[previous_hit_frame_number]
                    saltie_hit.previous_hit = previous_saltie_hit
            except IndexError:
                pass

            # next hit
            next_saltie_hit = None
            try:
                next_hit_frame_number = hit_frame_numbers[hit_number + 1]
                if get_goal_number(next_hit_frame_number, saltie_game) == saltie_hit_goal_number:
                    next_saltie_hit = hit_analytics_dict[next_hit_frame_number]
                    saltie_hit.next_hit = next_saltie_hit
            except IndexError:
                pass

            # hit distance
            if next_saltie_hit:
                displacement = next_saltie_hit.hit.ball_data[['pos_x', 'pos_y', 'pos_z']].values - \
                               saltie_hit.hit.ball_data[['pos_x', 'pos_y', 'pos_z']].values
                hit_analytics_dict[hit]['distance'] = np.sqrt(np.square(displacement).sum())
            elif hit_analytics_dict[hit]['goal']:

                hit_analytics_dict[hit]['distance'] = 0

            if next_saltie_hit:
                if hit.player is next_saltie_hit.player:
                    if not hit_analytics_dict[hit]['dribble_continuation']:
                        hit_analytics_dict[hit]['dribble'] = True
                        hit_analytics_dict[next_saltie_hit]['dribble_continuation'] = True
                elif hit.player.is_orange == next_saltie_hit.player.is_orange:
                    hit_analytics_dict[hit]['pass_'] = True
                    hit_analytics_dict[next_saltie_hit]['passed'] = True

                    next_player_scores = False
                    next_player_goal_hit = None
                    i = 1
                    while True:
                        try:
                            _next_next_hit_frame_number = hit_frame_numbers[hit_number + i]
                            _next_next_hit = saltie_game.hits[_next_next_hit_frame_number]
                            if _next_next_hit.player is not next_saltie_hit.player:
                                break
                            if hit_analytics_dict[_next_next_hit]['goal']:
                                next_player_scores = True
                                next_player_goal_hit = _next_next_hit
                                break
                            i += 1
                        except IndexError:
                            break

                    if next_player_scores:
                        hit_analytics_dict[hit]['assist'] = True
                        hit_analytics_dict[next_player_goal_hit]['assisted'] = True
                        print('Found assist (%s) for goal (%s)' % (hit, next_saltie_hit))

        # find shots
        for hit in saltie_game.hits.values():
            ball_sim = BallSimulator(hit.ball_data, hit.player.is_orange)
            is_shot = ball_sim.get_is_shot()
            if is_shot:
                hit_analytics_dict[hit]['shot'] = True
                if hit_analytics_dict[hit]['goal']:
                    print('Found shot for goal:', hit)
            if hit_analytics_dict[hit]['goal'] and not is_shot:
                print('Goal is not shot: %s' % hit)


def get_goal_number(frame_number: int, saltie_game: SaltieGame) -> int:
    return saltie_game.data_frame.loc[frame_number, 'goal_number']
