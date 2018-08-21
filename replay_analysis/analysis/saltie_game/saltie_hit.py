import logging
from typing import Dict, TYPE_CHECKING, List
from bisect import bisect_left
import numpy as np

from replay_analysis.generated.api import game_pb2
from replay_analysis.generated.api.player_pb2 import Player
from replay_analysis.generated.api.stats.events_pb2 import Hit
from replay_analysis.json_parser.game import Game
from ..hit_detection.base_hit import BaseHit
from ..simulator.ball_simulator import BallSimulator
from ..simulator.map_constants import *

if TYPE_CHECKING:
    from .saltie_game import SaltieGame

logger = logging.getLogger(__name__)


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

    @staticmethod
    def get_distance_to_goal(game: Game, hit: Hit, player_map: Dict[str, Player]):
        ball_data = BaseHit.get_ball_data(game, hit)
        _goal_x = min(max(ball_data['pos_x'], GOAL_X / 2), -GOAL_X / 2)
        _goal_y = -MAP_Y / 2 if player_map[hit.player_id.id].is_orange else MAP_Y / 2

        displacement = ball_data[['pos_x', 'pos_y']].values - (_goal_x, _goal_y)
        distance = np.sqrt(np.square(displacement).sum())

        return distance

    @staticmethod
    def get_saltie_hits_from_game(game: Game, proto_game: game_pb2.Game, hits: Dict[int, Hit],
                                  player_map: Dict[str, Player], data_frames, kickoff_frames) -> Dict[int, 'SaltieHit']:
        hit_analytics_dict: Dict[int, Hit] = {}
        for hit in hits.values():
            hit.distance_to_goal = SaltieHit.get_distance_to_goal(game, hit, player_map)
            hit_analytics_dict[hit.frame_number] = hit

        hit_frame_numbers = sorted(hit_analytics_dict)

        SaltieHit.find_goal_hits(proto_game, kickoff_frames, hit_frame_numbers, hit_analytics_dict)

        # find passes and assists
        for hit_number in range(len(hit_frame_numbers)):
            hit_frame_number = hit_frame_numbers[hit_number]
            saltie_hit = hit_analytics_dict[hit_frame_number]

            saltie_hit_goal_number = get_goal_number(hit_frame_number, proto_game)
            # previous hit
            previous_saltie_hit = None
            try:
                previous_hit_frame_number = hit_frame_numbers[hit_number - 1]
                if get_goal_number(previous_hit_frame_number, proto_game) == saltie_hit_goal_number:
                    previous_saltie_hit = hit_analytics_dict[previous_hit_frame_number]
                    saltie_hit.previous_hit = previous_saltie_hit
            except IndexError:
                pass

            # next hit
            next_saltie_hit = None
            try:
                next_hit_frame_number = hit_frame_numbers[hit_number + 1]
                if get_goal_number(next_hit_frame_number, proto_game) == saltie_hit_goal_number:
                    next_saltie_hit = hit_analytics_dict[next_hit_frame_number]
                    saltie_hit.next_hit = next_saltie_hit
            except IndexError:
                pass

            # hit distance
            if next_saltie_hit:
                displacement = next_saltie_hit.hit.ball_data[['pos_x', 'pos_y', 'pos_z']].values - \
                               saltie_hit.hit.ball_data[['pos_x', 'pos_y', 'pos_z']].values
                saltie_hit.distance = np.sqrt(np.square(displacement).sum())
            elif saltie_hit.goal:
                saltie_hit.distance = 0

            if next_saltie_hit:
                if saltie_hit.hit.player is next_saltie_hit.hit.player:
                    if not saltie_hit.dribble_continuation:
                        saltie_hit.dribble = True
                        next_saltie_hit.dribble_continuation = True
                elif saltie_hit.hit.player.is_orange == next_saltie_hit.hit.player.is_orange:
                    saltie_hit.pass_ = True
                    next_saltie_hit.passed = True

                    next_player_scores = False
                    next_player_goal_hit = None
                    i = 1
                    while True:
                        try:
                            _next_next_hit_frame_number = hit_frame_numbers[hit_number + i]
                            _next_next_saltie_hit = hit_analytics_dict[_next_next_hit_frame_number]
                            if _next_next_saltie_hit.hit.player is not next_saltie_hit.hit.player:
                                break
                            if _next_next_saltie_hit.goal:
                                next_player_scores = True
                                next_player_goal_hit = _next_next_saltie_hit
                                break
                            i += 1
                        except IndexError:
                            break

                    if next_player_scores:
                        saltie_hit.assist = True
                        next_player_goal_hit.assisted = True
                        logger.info('Found assist (%s) for goal (%s)' % (saltie_hit.hit, next_saltie_hit.hit))

        # find shots
        # TODO: Support non-standard maps? Raise warning/don't predict for non-standard maps?
        for saltie_hit in hit_analytics_dict.values():
            ball_sim = BallSimulator(saltie_hit.hit.ball_data, saltie_hit.hit.player.is_orange)
            is_shot = ball_sim.get_is_shot()
            if is_shot:
                saltie_hit.shot = True
                if saltie_hit.goal:
                    logger.info('Found shot for goal: %s', saltie_hit.hit)
            if saltie_hit.goal and not is_shot:
                logger.warning('Goal is not shot: %s' % saltie_hit.hit)

        return hit_analytics_dict

    @staticmethod
    def find_goal_hits(proto_game: game_pb2, kickoff_frames, sorted_frames: List[int], hit_analytics_dict: [int, Hit]):
        total_frames = len(sorted_frames)
        end_search = 0
        # find last hit by goalscorer for each goal frame
        for goal_number, goal in enumerate(proto_game.game_metadata.goals):
            goal_kickoff_frame = int(kickoff_frames[goal_number])
            last_goalscorer_saltie_hit = None
            # Only look for the frames that occur right before the goal.
            start_search = bisect_left(sorted_frames, goal.frame, 0, total_frames - 1)
            for frame_index in range(start_search, end_search, -1):
                frame_number = sorted_frames[frame_index]
                saltie_hit = hit_analytics_dict[frame_number]
                if not (goal_kickoff_frame <= saltie_hit.frame_number <= goal.frame):
                    continue
                if saltie_hit.player_id.id == goal.player_id.id:
                    last_goalscorer_saltie_hit = saltie_hit
                    break
            end_search = start_search
            if last_goalscorer_saltie_hit is None:
                logger.warning("Could not find hit for goal: %s" % goal)
            else:
                last_goalscorer_saltie_hit.goal = True
                logger.debug("Found hit for goal on frame %s: %s" % (goal.frame, last_goalscorer_saltie_hit))


def get_goal_number(frame_number: int, saltie_game: 'SaltieGame') -> int:
    return saltie_game.data_frame['game']['goal_number'].loc[frame_number]
