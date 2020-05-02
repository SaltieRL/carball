import logging
import time
from typing import Dict, List
from bisect import bisect_left

from ....generated.api import game_pb2
from ....generated.api.player_pb2 import Player
from ....generated.api.stats.events_pb2 import Hit
from carball.analysis.events.hit_detection.base_hit import BaseHit
from carball.analysis.simulator.ball_simulator import BallSimulator
from carball.analysis.simulator.map_constants import *
from carball.analysis.constants.field_constants import *


logger = logging.getLogger(__name__)


class SaltieHit:

    @staticmethod
    def get_distance_to_goal(data_frame: pd.DataFrame, hit: Hit, player_map: Dict[str, Player]):
        ball_data = BaseHit.get_ball_data(data_frame, hit)
        _goal_x = min(max(ball_data['pos_x'], GOAL_X / 2), -GOAL_X / 2)
        _goal_y = -MAP_Y / 2 if player_map[hit.player_id.id].is_orange else MAP_Y / 2

        displacement = ball_data[['pos_x', 'pos_y']].values - (_goal_x, _goal_y)
        distance = np.sqrt(np.square(displacement).sum())

        return distance

    @staticmethod
    def get_saltie_hits_from_game(proto_game: game_pb2.Game, hits: Dict[int, Hit],
                                  player_map: Dict[str, Player], data_frame: pd.DataFrame,
                                  kickoff_frames: pd.DataFrame) -> Dict[int, Hit]:
        hit_analytics_dict: Dict[int, Hit] = hits

        sorted_frames = sorted(hit_analytics_dict)

        start_time = time.time()
        SaltieHit.find_goal_hits(proto_game, kickoff_frames, sorted_frames, hit_analytics_dict)
        total_time = time.time() - start_time
        logger.debug('goal time: %s', total_time * 1000)

        SaltieHit.find_hit_stats(data_frame, player_map, sorted_frames, hit_analytics_dict)

        return hit_analytics_dict

    @staticmethod
    def find_goal_hits(proto_game: game_pb2.Game, kickoff_frames: pd.DataFrame,
                       sorted_frames: List[int], hit_analytics_dict: [int, Hit]):
        total_frames = len(sorted_frames)
        end_search = 0
        # find last hit by goalscorer for each goal frame
        for goal_number, goal in enumerate(proto_game.game_metadata.goals):
            goal_kickoff_frame = int(kickoff_frames[goal_number])
            last_goalscorer_saltie_hit = None
            # Only look for the frames that occur right before the goal.
            start_search = bisect_left(sorted_frames, goal.frame_number, end_search, total_frames - 1)
            for frame_index in range(start_search, end_search, -1):
                frame_number = sorted_frames[frame_index]
                saltie_hit = hit_analytics_dict[frame_number]
                if not (goal_kickoff_frame <= saltie_hit.frame_number <= goal.frame_number):
                    continue
                if saltie_hit.player_id.id == goal.player_id.id:
                    last_goalscorer_saltie_hit = saltie_hit
                    break
            end_search = start_search
            if last_goalscorer_saltie_hit is None:
                logger.warning("Could not find hit for goal: %s", goal)
            else:
                last_goalscorer_saltie_hit.goal = True
                # logger.debug("Found hit for goal on frame %s: %s", goal.frame_number, last_goalscorer_saltie_hit)

    @staticmethod
    def next_hit_stats(data_frame: pd.DataFrame, saltie_hit: Hit, next_saltie_hit: Hit,
                       player_map: Dict[str, Player], last_passing_hit: Hit):
        """
        finds stats that happen based off of the next hit.
        Passes, dribbles are found here, also candidates for assists.
        :param game:
        :param saltie_hit:
        :param next_saltie_hit:
        :param player_map:
        :param last_passing_hit:
        :return:
        """

        # distance the ball traveled
        displacement = (BaseHit.get_ball_data(data_frame, next_saltie_hit)[['pos_x', 'pos_y', 'pos_z']].values -
                        BaseHit.get_ball_data(data_frame, saltie_hit)[['pos_x', 'pos_y', 'pos_z']].values)
        saltie_hit.distance = np.sqrt(np.square(displacement).sum())

        # dribble detection
        if saltie_hit.player_id.id == next_saltie_hit.player_id.id:
            if not saltie_hit.dribble_continuation:
                saltie_hit.dribble = True
                next_saltie_hit.dribble_continuation = True
        else:
            last_passing_hit = None
            # passing detection
            if player_map[saltie_hit.player_id.id].is_orange == player_map[next_saltie_hit.player_id.id].is_orange:
                saltie_hit.pass_ = True
                next_saltie_hit.passed = True
                last_passing_hit = saltie_hit

        return last_passing_hit

    @staticmethod
    def get_shot(data_frame: pd.DataFrame, saltie_hit: Hit, player_map: Dict[str, Player]):
        """
        Finds shots using ball prediction.
        :param game:
        :param saltie_hit:
        :param player_map:
        """
        # find shots
        # TODO: Support non-standard maps? Raise warning/don't predict for non-standard maps?
        player = player_map[saltie_hit.player_id.id]
        ball_sim = BallSimulator(BaseHit.get_ball_data(data_frame, saltie_hit),
                                 player.is_orange)
        is_shot = ball_sim.get_is_shot()
        if is_shot:
            saltie_hit.shot = True
            # if saltie_hit.goal:
            #    logger.debug('Found shot for goal:')
        if saltie_hit.goal and not is_shot:
            logger.warning(f'Goal is not shot: frame {saltie_hit.frame_number} by {player.name}')

    @staticmethod
    def get_clear(data_frame: pd.DataFrame, saltie_hit: Hit, next_saltie_hit: Hit,  player_map: Dict[str, Player]):
        """
        Finds clears based on distance travelled and positions.
        :param game:
        :param saltie_hit:
        :param next_saltie_hit:
        :param player_map:
        """
        CLEAR_BUFFER = 400
        player =  player_map[saltie_hit.player_id.id]

        # get y-pos of ball to determine if the hit occurs in a player's defending third
        y_pos = saltie_hit.ball_data.pos_y
        defending_on_orange = (player.is_orange and y_pos > (STANDARD_FIELD_LENGTH_HALF/3 + CLEAR_BUFFER))
        defending_on_blue = (not player.is_orange and y_pos < ((-1)*STANDARD_FIELD_LENGTH_HALF/3 - CLEAR_BUFFER))

        # make sure the player is in their own defending third
        if not (defending_on_orange or defending_on_blue):
            return

        # determine if hit passed the buffer to be considered a clear
        if next_saltie_hit is not None:

            # check edge case where an own goal moves the ball to the middle
            goals_at_hit = data_frame.game.loc[saltie_hit.frame_number].goal_number
            goals_at_next_hit = data_frame.game.loc[next_saltie_hit.frame_number].goal_number
            if goals_at_hit != goals_at_next_hit:
                # lol they own-goaled
                return

            # find next hit, determine if this hit went far enough
            next_y = next_saltie_hit.ball_data.pos_y
            orange_reached_neutral_third = (player.is_orange and next_y < (STANDARD_FIELD_LENGTH_HALF/3 - CLEAR_BUFFER))
            blue_reached_neutral_third = (not player.is_orange and next_y > ((-1)*STANDARD_FIELD_LENGTH_HALF/3 + CLEAR_BUFFER))
            if orange_reached_neutral_third or blue_reached_neutral_third:
                saltie_hit.clear = True

        else:
            # a big hit to end the game should also count as a clear
            distance = saltie_hit.distance
            if distance > CLEAR_BUFFER:
                saltie_hit.clear = True

    @staticmethod
    def find_hit_stats(data_frame: pd.DataFrame, player_map: Dict[str, Player],
                       sorted_frames, hit_analytics_dict: Dict[int, Hit]):
        """
        Finds stats for all hits.
        :param data_frame:
        :param player_map:
        :param sorted_frames:
        :param hit_analytics_dict:
        """

        last_passing_hit = None
        total_stat_time = 0
        total_next_hit_time = 0
        total_simulation_time = 0
        for hit_number in range(len(sorted_frames)):
            start_time = time.time()
            hit_frame_number = sorted_frames[hit_number]
            saltie_hit: Hit = hit_analytics_dict[hit_frame_number]

            saltie_hit_goal_number = saltie_hit.goal_number
            # previous hit
            try:
                previous_hit_frame_number = sorted_frames[hit_number - 1]
                previous_saltie_hit = hit_analytics_dict[previous_hit_frame_number]
                if previous_saltie_hit.goal_number == saltie_hit_goal_number:
                    previous_saltie_hit = hit_analytics_dict[previous_hit_frame_number]
                    saltie_hit.previous_hit_frame_number = previous_saltie_hit.frame_number
            except IndexError:
                pass

            # next hit
            next_saltie_hit = None
            try:
                next_hit_frame_number = sorted_frames[hit_number + 1]
                next_saltie_hit = hit_analytics_dict[next_hit_frame_number]
                if next_saltie_hit.goal_number == saltie_hit_goal_number:
                    next_saltie_hit = hit_analytics_dict[next_hit_frame_number]
                    saltie_hit.next_hit_frame_number = next_saltie_hit.frame_number
            except IndexError:
                pass

            next_hit_time = time.time()
            total_next_hit_time += next_hit_time - start_time

            # aerials
            if saltie_hit.ball_data.pos_z >= 400.0:
                saltie_hit.aerial = True

            # assist calculation
            if saltie_hit.goal and last_passing_hit is not None:
                saltie_hit.assisted = True
                last_passing_hit.assist = True
                logger.debug('Found assist (%s) for goal', last_passing_hit.frame_number)

            # hit distance
            if next_saltie_hit:
                last_passing_hit = SaltieHit.next_hit_stats(data_frame, saltie_hit, next_saltie_hit,
                                                            player_map, last_passing_hit)
            elif saltie_hit.goal:
                saltie_hit.distance = 0

            stat_time = time.time()
            total_stat_time += stat_time - next_hit_time

            saltie_hit.distance_to_goal = SaltieHit.get_distance_to_goal(data_frame, saltie_hit, player_map)

            SaltieHit.get_shot(data_frame, saltie_hit, player_map)
            SaltieHit.get_clear(data_frame, saltie_hit, next_saltie_hit, player_map)

            simulation_time = time.time()
            total_simulation_time += simulation_time - stat_time

            try:
                if player_map[previous_saltie_hit.player_id.id].is_orange != player_map[saltie_hit.player_id.id].is_orange:
                    if previous_saltie_hit.shot and not previous_saltie_hit.goal:
                        saltie_hit.save = True
            except NameError:
                pass

        logger.debug('next time: %s', total_next_hit_time * 1000)
        logger.debug('stat time: %s', total_stat_time * 1000)
        logger.debug('sim  time: %s', total_simulation_time * 1000)
