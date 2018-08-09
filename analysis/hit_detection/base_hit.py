from typing import List, Dict

import numpy as np
import pandas as pd

from json_parser.game import Game
from .hitbox.car import get_hitbox, get_distance

COLLISION_DISTANCE_HIGH_LIMIT = 500
COLLISION_DISTANCE_LOW_LIMIT = 250


class BaseHit:
    def __init__(self, game: Game, frame_number=None, player=None, collision_distance=9999):

        self.frame_number = frame_number
        self.player = player
        self.collision_distance = collision_distance

        if self.player != 'unknown':
            self.player_data = self.player.data.loc[self.frame_number, :]

        self.ball_data = game.ball.loc[self.frame_number, :]
        i = 10
        while i < 20:
            try:
                self.post_hit_ball_data = game.ball.loc[self.frame_number + i, :]
                break
            except KeyError:
                i += 1
        i = 10
        while i < 20:
            try:
                self.pre_hit_ball_data = game.ball.loc[self.frame_number - i, :]
                break
            except KeyError:
                i += 1

    def __repr__(self):
        return 'Hit by %s on frame %s at distance %i' % (self.player, self.frame_number, self.collision_distance)

    @staticmethod
    def get_hits_from_game(game: Game) -> Dict[int, 'BaseHit']:
        team_dict = {}
        all_hits = {}  # frame_number: [{hit_data}, {hit_data}] for hit guesses
        for team in game.teams:
            team_dict[team.is_orange] = team

        hit_frame_numbers = BaseHit.get_hit_frame_numbers_by_ball_ang_vel(game)

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

            if closest_player_distance < COLLISION_DISTANCE_HIGH_LIMIT:
                hit_player = closest_player
                hit_collision_distance = closest_player_distance
            else:
                hit_player = None
                hit_collision_distance = 999999

            if hit_player is not None:
                hit = BaseHit(game, frame_number=frame_number, player=hit_player,
                              collision_distance=hit_collision_distance)
                all_hits[frame_number] = hit

        return all_hits

    @staticmethod
    def get_hit_frame_numbers_by_ball_ang_vel(game: Game) -> List[int]:
        ball_ang_vels = game.ball.loc[:, ['ang_vel_x', 'ang_vel_y', 'ang_vel_z']]
        diff_series = ball_ang_vels.fillna(0).diff().any(axis=1)
        indices = diff_series.index[diff_series].tolist()
        return indices


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
