
import logging
import time
from typing import List, Dict, Callable

import numpy as np
import pandas as pd

from .hitbox.hitbox import Hitbox
from ...generated.api import game_pb2
from ...generated.api.stats.events_pb2 import Hit
from ...json_parser.game import Game

logger = logging.getLogger(__name__)


class BaseHit:

    @staticmethod
    def get_hits_from_game(game: Game, proto_game: game_pb2, id_creation: Callable,
                           data_frame: pd.DataFrame) -> Dict[int, Hit]:

        start_time = time.time()

        team_dict = {}

        for team in game.teams:
            team_dict[team.is_orange] = team

        hit_frame_numbers = BaseHit.get_hit_frame_numbers_by_ball_ang_vel(data_frame)

        hit_creation_time = time.time()
        logger.info('time to get get frame_numbers: %s', (hit_creation_time - start_time) * 1000)

        positional_columns = ['pos_x', 'pos_y', 'pos_z', 'rot_x', 'rot_y', 'rot_z']
        hit_frames = data_frame.loc[hit_frame_numbers, (slice(None), positional_columns)]
        player_displacements = {player.name: get_player_ball_displacements(hit_frames, player.name)
                                for player in game.players}

        # player_distances = {player_name: get_distance_from_displacements(data_frame).rename(player_name)
        #                     for player_name, data_frame in player_displacements.items()}

        # player_distances_data_frame = pd.concat(player_distances, axis=1)

        rotation_matrices = {player.name: get_rotation_matrices(hit_frames, player.name) for player in game.players}

        local_displacements: Dict[str, pd.DataFrame] = {
            player.name: get_local_displacement(player_displacements[player.name],
                                                rotation_matrices[player.name])
            for player in game.players
        }

        player_hitboxes = get_player_hitboxes(game)
        collision_distances = [
            get_collision_distances(local_displacements[player.name], player_hitboxes[player.name]).rename(player.name)
            for player in game.players
        ]
        collision_distances_data_frame = pd.concat(collision_distances, axis=1)

        player_name_to_team: Dict[str, int] = {player.name: int(player.team.is_orange) for player in game.players}
        columns = [(player_name_to_team[player_name], player_name)
                   for player_name in collision_distances_data_frame.columns]
        collision_distances_data_frame.columns = pd.MultiIndex.from_tuples(columns)

        collision_distances_data_frame['closest_player', 'name'] = None
        collision_distances_data_frame['closest_player', 'distance'] = None
        for hit_team_no in [0, 1]:
            collision_distances_for_team = collision_distances_data_frame[
                hit_team_no].loc[data_frame.ball['hit_team_no'] == hit_team_no]

            close_collision_distances_for_team = collision_distances_for_team[
                (collision_distances_for_team < 300).any(axis=1)
            ]

            collision_distances_data_frame['closest_player', 'distance'].fillna(
                close_collision_distances_for_team.min(axis=1),
                inplace=True
            )
            collision_distances_data_frame['closest_player', 'name'].fillna(
                close_collision_distances_for_team.idxmin(axis=1),
                inplace=True
            )

        all_hits = {}
        hits_data = collision_distances_data_frame['closest_player'].dropna()

        hit_frames_to_keep = []
        for row in hits_data.itertuples():
            frame_number, player_name, collision_distance = row.Index, row.name, row.distance
            # Remove frame numbers where there is a hit in the next or previous frame by the same player
            # and player is closer in that (next or previous) hit frame.
            try:
                previous_frame_hit = hits_data.loc[frame_number - 1]
                if previous_frame_hit.loc['name'] == player_name and previous_frame_hit.distance < collision_distance:
                    continue
            except KeyError:
                pass
            try:
                next_frame_hit = hits_data.loc[frame_number + 1]
                if next_frame_hit.loc['name'] == player_name and next_frame_hit.distance < collision_distance:
                    continue
            except KeyError:
                pass

            hit_frames_to_keep.append(frame_number)

        hits_data = hits_data.loc[hit_frames_to_keep]

        for row in hits_data.itertuples():
            frame_number, player_name, collision_distance = row.Index, row.name, row.distance
            hit = proto_game.game_stats.hits.add()
            hit.frame_number = frame_number
            goal_number = data_frame.at[frame_number, ('game', 'goal_number')]
            if not np.isnan(goal_number):
                hit.goal_number = int(goal_number)
            id_creation(hit.player_id, player_name)
            hit.collision_distance = collision_distance
            ball_position = data_frame.ball.loc[frame_number, ['pos_x', 'pos_y', 'pos_z']]
            hit.ball_data.pos_x = float(ball_position['pos_x'])
            hit.ball_data.pos_y = float(ball_position['pos_y'])
            hit.ball_data.pos_z = float(ball_position['pos_z'])
            all_hits[frame_number] = hit

        time_diff = time.time() - hit_creation_time
        logger.info('ball hit creation time: %s', time_diff * 1000)
        return all_hits

    @staticmethod
    def get_hit_frame_numbers_by_ball_ang_vel(data_frame: pd.DataFrame) -> List[int]:
        ball_ang_vels = data_frame.ball.loc[:, ['ang_vel_x', 'ang_vel_y', 'ang_vel_z']]
        diff_series = ball_ang_vels.diff().any(axis=1)
        indices = diff_series.index[diff_series].tolist()
        return indices

    @staticmethod
    def get_ball_data(data_frame: pd.DataFrame, hit: Hit):
        return data_frame.ball.loc[hit.frame_number, :]


def get_player_ball_displacements(data_frame: pd.DataFrame, player_name: str) -> pd.DataFrame:
    player_df = data_frame[player_name]
    ball_df = data_frame['ball']
    position_column_names = ['pos_x', 'pos_y', 'pos_z']
    return player_df[position_column_names] - ball_df[position_column_names]


def get_distance_from_displacements(data_frame: pd.DataFrame) -> pd.Series:
    position_column_names = ['pos_x', 'pos_y', 'pos_z']
    return np.sqrt((data_frame[position_column_names] ** 2).sum(axis=1))


def get_rotation_matrices(data_frame: pd.DataFrame, player_name: str) -> pd.Series:
    pitch = data_frame[player_name, 'rot_x']
    yaw = data_frame[player_name, 'rot_y']
    roll = data_frame[player_name, 'rot_z']

    cos_roll = np.cos(roll).rename('cos_roll')
    sin_roll = np.sin(roll).rename('sin_roll')
    cos_pitch = np.cos(pitch).rename('cos_pitch')
    sin_pitch = np.sin(pitch).rename('sin_pitch')
    cos_yaw = np.cos(yaw).rename('cos_yaw')
    sin_yaw = np.sin(yaw).rename('sin_yaw')

    components: pd.DataFrame = pd.concat([cos_roll, sin_roll, cos_pitch, sin_pitch, cos_yaw, sin_yaw], axis=1)

    rotation_matrix = components.apply(get_rotation_matrix_from_row, axis=1, result_type='reduce')
    return rotation_matrix


def get_rotation_matrix_from_row(components: pd.Series) -> np.array:
    cos_roll, sin_roll, cos_pitch, sin_pitch, cos_yaw, sin_yaw = components.values
    rotation_matrix = np.array(
        [[cos_pitch * cos_yaw, cos_yaw * sin_pitch * sin_roll - cos_roll * sin_yaw,
          -cos_roll * cos_yaw * sin_pitch - sin_roll * sin_yaw],
         [cos_pitch * sin_yaw, sin_yaw * sin_pitch * sin_roll + cos_roll * cos_yaw,
          -cos_roll * sin_yaw * sin_pitch + sin_roll * cos_yaw],
         [sin_pitch, -cos_pitch * sin_roll, cos_pitch * cos_roll]])
    return rotation_matrix


def get_local_displacement(displacement: pd.DataFrame, rotation_matrices: pd.Series) -> pd.DataFrame:
    position_column_names = ['pos_x', 'pos_y', 'pos_z']
    displacement_vectors = np.expand_dims(displacement[position_column_names].values, 2)
    inverse_rotation_matrices: pd.Series = np.transpose(rotation_matrices)
    inverse_rotation_array = np.stack(inverse_rotation_matrices.values)
    local_displacement = np.matmul(inverse_rotation_array, displacement_vectors)
    displacement_data_frame = pd.DataFrame(data=np.squeeze(local_displacement, 2),
                                           index=displacement.index,
                                           columns=position_column_names)
    return displacement_data_frame


def get_player_hitboxes(game: Game) -> Dict[str, Hitbox]:
    player_hitboxes = {}
    for player in game.players:
        car_item_id = player.loadout[0]['car'] if len(player.loadout) == 1 else player.loadout[player.is_orange]['car']
        player_hitboxes[player.name] = Hitbox(car_item_id)
    return player_hitboxes


def get_collision_distances(local_ball_displacement: pd.DataFrame, player_hitbox: Hitbox) -> pd.Series:
    def get_distance_function_for_player(displacement: pd.Series):
        return player_hitbox.get_collision_distance(displacement.values)

    collision_distances = local_ball_displacement.apply(get_distance_function_for_player, axis=1, result_type='reduce')
    return collision_distances
