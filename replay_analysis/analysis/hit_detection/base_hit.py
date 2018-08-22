import math
import time
from typing import List, Dict, Callable
import logging

import numpy as np
import pandas as pd

from replay_analysis.generated.api import game_pb2
from replay_analysis.generated.api.stats.events_pb2 import Hit
from replay_analysis.json_parser.game import Game
from .hitbox.car import get_hitbox, get_distance

COLLISION_DISTANCE_HIGH_LIMIT = 500
COLLISION_DISTANCE_LOW_LIMIT = 250

logger = logging.getLogger(__name__)


class BaseHit:

    @staticmethod
    def get_hits_from_game(game: Game, proto_game: game_pb2, id_creation: Callable, data_frames) -> Dict[int, Hit]:

        start_time = time.time()

        team_dict = {}
        all_hits = {}  # frame_number: [{hit_data}, {hit_data}] for hit guesses
        for team in game.teams:
            team_dict[team.is_orange] = team

        hit_frame_numbers = BaseHit.get_hit_frame_numbers_by_ball_ang_vel(game)
        frame_slice = (slice(None), ['pos_x', 'pos_y', 'pos_z', 'rot_x', 'rot_y', 'rot_z', 'goal_number', 'hit_team_no'])
        location_slice = ['pos_x', 'pos_y', 'pos_z']
        rotation_slice = ['rot_x', 'rot_y', 'rot_z']

        hit_creation_time = time.time()
        logger.info('time to get get frame_numbers: %s', (hit_creation_time - start_time) * 1000)

        # find closest player in team to ball for known hits
        for frame_number in hit_frame_numbers:
            try:
                team = team_dict[game.ball.loc[frame_number, 'hit_team_no']]
            except KeyError:
                continue
            closest_player = None
            closest_player_distance = 999999
            for player in team.players:
                if len(player.loadout) == 1:
                    player_hitbox = get_hitbox(player.loadout[0]['car'])
                else:
                    player_hitbox = get_hitbox(player.loadout[player.is_orange]['car'])
                try:
                    player_position = player.data.loc[frame_number, ['pos_x', 'pos_y', 'pos_z']]
                    ball_position = game.ball.loc[frame_number, ['pos_x', 'pos_y', 'pos_z']]
                    ball_displacement = ball_position - player_position

                    player_rotation = player.data.loc[frame_number, ['rot_x', 'rot_y', 'rot_z']]
                except KeyError:
                    continue

                joined = pd.concat([player_rotation, ball_displacement])
                joined.dropna(inplace=True)
                if joined.any():
                    ball_displacement = joined.loc[['pos_x', 'pos_y', 'pos_z']].values
                    player_rotation = joined.loc[['rot_x', 'rot_y', 'rot_z']].values
                    ball_unrotated_displacement = unrotate_position(ball_displacement, player_rotation)

                    collision_distance = get_distance(ball_unrotated_displacement, player_hitbox)
                    if collision_distance < closest_player_distance:
                        closest_player = player
                        closest_player_distance = collision_distance

            # TODO: Check if this works with ball_type == 'Basketball'
            # COLLISION_DISTANCE_HIGH_LIMIT probably needs to be increased if Basketball.
            if closest_player_distance < COLLISION_DISTANCE_HIGH_LIMIT:
                hit_player = closest_player
                hit_collision_distance = closest_player_distance
            else:
                hit_player = None
                hit_collision_distance = 999999

            if hit_player is not None:
                hit = proto_game.game_stats.hits.add()
                hit.frame_number = frame_number
                goal_number = data_frames.at[frame_number, ('game', 'goal_number')]
                if not math.isnan(goal_number):
                    hit.goal_number = int(goal_number)
                id_creation(hit.player_id, hit_player.name)
                hit.collision_distance = hit_collision_distance
                all_hits[frame_number] = hit

        time_diff = time.time() - hit_creation_time
        logger.info('ball hit creation time: %s', time_diff * 1000)
        return all_hits

    @staticmethod
    def get_hit_frame_numbers_by_ball_ang_vel(game) -> List[int]:
        ball_ang_vels = game.ball.loc[:, ['ang_vel_x', 'ang_vel_y', 'ang_vel_z']]
        diff_series = ball_ang_vels.diff().any(axis=1)
        indices = diff_series.index[diff_series].tolist()
        return indices

    @staticmethod
    def get_ball_data(game: Game, hit: Hit):
        return game.ball.loc[hit.frame_number, :]


def unrotate_position(relative_position, rotation):
    # TODO: Use rotation matrix
    new_position = relative_position

    # YAW
    yaw = rotation[1]
    yaw = -yaw * np.pi

    new_position[0], new_position[1] = new_position[0] * np.cos(yaw) - new_position[1] * np.sin(yaw), new_position[
        0] * np.sin(yaw) + new_position[1] * np.cos(yaw)

    # PITCH

    pitch = rotation[0]
    pitch = pitch * np.pi / 2

    new_position[0], new_position[0] = new_position[2] * np.cos(pitch) - new_position[0] * np.sin(pitch), new_position[
        2] * np.sin(pitch) + new_position[0] * np.cos(pitch)

    # ROLL

    roll = rotation[2]
    roll = roll * np.pi

    new_position[1], new_position[2] = new_position[1] * np.cos(roll) - new_position[2] * np.sin(roll), new_position[
        1] * np.sin(roll) + new_position[2] * np.cos(roll)

    return new_position
