import numpy as np
import pandas as pd
from .hitbox.car import get_hitbox, get_distance
from .bouncer.ball import Ball, check_ball_collision
from utils import utils
from .map_constants import *

COLLISION_DISTANCE_HIGH_LIMIT = 500
COLLISION_DISTANCE_LOW_LIMIT = 250


class Hit:
    def __init__(self, game, frame_number=None, player=None, collision_distance=9999):

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

        game.hits[frame_number] = self

    def __repr__(self):
        return 'Hit by %s on frame %s at distance %i' % (self.player, self.frame_number, self.collision_distance)

    @staticmethod
    def add_hits_to_game(game):
        game.hits = {}  # frame_number: hit
        team_dict = {}
        all_hits = {}  # frame_number: [{hit_data}, {hit_data}] for hit guesses
        for team in game.teams:
            team_dict[team.is_orange] = team

        ball_ang_vels = game.ball.loc[:, ['ang_vel_x', 'ang_vel_y', 'ang_vel_z']]
        diff_series = ball_ang_vels.fillna(0).diff().any(axis=1)
        indices = diff_series.index[diff_series].tolist()
        # print(indices)
        # print(len(indices))
        ball_positions = game.ball.loc[indices, ['pos_x', 'pos_y', 'pos_z']]
        for frame_number, frame_data in ball_positions.iterrows():
            collided = check_ball_collision(frame_data.values)
            # print(collided)
            # print(frame_data.values)
            if collided:
                # indices.remove(frame_number)
                pass
        # print(indices)
        # print(len(indices))

        # find closest player in team to ball for known hits
        for frame_number in indices:
            try:
                team = team_dict[game.ball.loc[frame_number, 'hit_team_no']]
            except KeyError:
                continue
            closest_player = None
            closest_player_distance = 999999
            collision_distances = {}
            for player in team.players:
                player_hitbox = get_hitbox(player.loadout[player.is_orange]['car'])

                player_position = player.data.loc[frame_number, ['pos_x', 'pos_y', 'pos_z']]
                ball_position = game.ball.loc[frame_number, ['pos_x', 'pos_y', 'pos_z']]
                ball_displacement = ball_position - player_position
                player_rotation = player.data.loc[frame_number, ['rot_x', 'rot_y', 'rot_z']]

                joined = pd.concat([player_rotation, ball_displacement])
                joined.dropna(inplace=True)
                if joined.any():
                    ball_displacement = joined.loc[['pos_x', 'pos_y', 'pos_z']].values
                    player_rotation = joined.loc[['rot_x', 'rot_y', 'rot_z']].values
                    ball_unrotated_displacement = utils.unrotate_position(ball_displacement, player_rotation)

                    collision_distance = get_distance(ball_unrotated_displacement, player_hitbox)
                    collision_distances[player] = collision_distance
                    if collision_distance < closest_player_distance:
                        closest_player = player
                        closest_player_distance = collision_distance

            if closest_player_distance < COLLISION_DISTANCE_HIGH_LIMIT:
                hit_player = closest_player
                hit_collision_distance = closest_player_distance
            else:
                hit_player = None
                hit_collision_distance = 999999
                # print(team)
                # print(collision_distances)

            if hit_player is not None:
                hit = Hit(game, frame_number=frame_number, player=hit_player,
                          collision_distance=hit_collision_distance)
                # print(hit)
                all_hits[frame_number] = hit

        return len(game.hits)

    @staticmethod
    def add_hits_to_game2(game):
        team_dict = {}
        all_hits = {}  # frame_number: [{hit_data}, {hit_data}] for hit guesses
        for team in game.teams:
            team_dict[team.is_orange] = team
        # find where hit_team_no changes
        last_hit_team_no = np.nan
        for frame_number, ball_row in game.ball.iterrows():
            hit_team_no = ball_row['hit_team_no']
            if hit_team_no != last_hit_team_no and not np.isnan(hit_team_no):
                all_hits[frame_number] = [{'type': 'known',
                                           'team': team_dict[hit_team_no],
                                           'frame_number': frame_number}]
            last_hit_team_no = hit_team_no

        # find all distances
        all_player_distances = {}
        ball_positions = game.ball.loc[:, ('pos_x', 'pos_y', 'pos_z')]
        for player in game.players:
            player_positions = player.data.loc[:, ('pos_x', 'pos_y', 'pos_z')]
            _player_axis_distances = (ball_positions - player_positions).dropna()
            distances = np.sqrt(np.square(_player_axis_distances).sum(axis=1))
            all_player_distances[player] = distances

        # find closest player in team to ball for known hits
        for frame_number, hits in all_hits.items():
            hit = hits[0]
            team = hit['team']
            # frame_number = hit['frame_number']
            closest_player = None
            closest_player_distance = 999999
            for player in team.players:
                player_hitbox = get_hitbox(player.loadout[player.is_orange]['car'])

                player_position = player.data.loc[frame_number, ['pos_x', 'pos_y', 'pos_z']]
                ball_position = game.ball.loc[frame_number, ['pos_x', 'pos_y', 'pos_z']]
                ball_displacement = ball_position - player_position
                player_rotation = player.data.loc[frame_number, ['rot_x', 'rot_y', 'rot_z']]

                joined = pd.concat([player_rotation, ball_displacement])
                joined.dropna(inplace=True)
                if joined.any():
                    ball_displacement = joined.loc[['pos_x', 'pos_y', 'pos_z']].values
                    player_rotation = joined.loc[['rot_x', 'rot_y', 'rot_z']].values
                    ball_unrotated_displacement = utils.unrotate_position(ball_displacement, player_rotation)

                    collision_distance = get_distance(ball_unrotated_displacement, player_hitbox)
                    if collision_distance < closest_player_distance:
                        closest_player = player
                        closest_player_distance = collision_distance

            if closest_player_distance < COLLISION_DISTANCE_HIGH_LIMIT:
                hit['player'] = closest_player
                hit['collision_distance'] = closest_player_distance
            else:
                hit['player'] = 'unknown'
                hit['collision_distance'] = 999999

        # find guessed hits
        for player, player_distances in all_player_distances.items():
            player_hitbox = get_hitbox(player.loadout[player.is_orange]['car'])
            filtered_frame_numbers = player_distances[player_distances < COLLISION_DISTANCE_HIGH_LIMIT].index.values

            player_positions = player.data.loc[filtered_frame_numbers, ['pos_x', 'pos_y', 'pos_z']]
            ball_positions = game.ball.loc[filtered_frame_numbers, ['pos_x', 'pos_y', 'pos_z']]
            ball_displacements = ball_positions - player_positions

            player_rotations = player.data.loc[:, ['rot_x', 'rot_y', 'rot_z']]

            # print(ball_positions.head(), player_rotations.head())
            joined = pd.DataFrame.join(player_rotations, ball_displacements)
            joined.dropna(inplace=True)
            # print(joined.head(), '\n\n\n')

            ball_displacements = joined.loc[:, ['pos_x', 'pos_y', 'pos_z']].values
            player_rotations = joined.loc[:, ['rot_x', 'rot_y', 'rot_z']].values
            ball_unrotated_displacements = utils.unrotate_positions(ball_displacements, player_rotations)

            player_hits = []
            for i, frame_number in enumerate(joined.index.values):
                collision_distance = get_distance(ball_unrotated_displacements[i], player_hitbox)
                position_distance = player_distances[frame_number]

                if collision_distance < COLLISION_DISTANCE_LOW_LIMIT:
                    hit = {'type': 'guessed',
                           'team': player.team,
                           'frame_number': frame_number,
                           'player': player,
                           'collision_distance': collision_distance,
                           'position_distance': position_distance}
                    if frame_number not in all_hits:
                        all_hits[frame_number] = [hit]
                    else:
                        hits = all_hits[frame_number]
                        # check if hit is already in all_hits[frame_number]
                        player_hit_already_exists = False
                        for i in range(len(hits)):
                            test_hit = hits[i]
                            if test_hit['player'] is player:
                                player_hit_already_exists = True
                                for key, value in hit.items():
                                    if key not in test_hit:
                                        test_hit[key] = value
                                break
                        if not player_hit_already_exists:
                            all_hits[frame_number].append(hit)
                    player_hits.append(hit)
            # print(player, len(player_hits))

        # create hit objects
        hit_objects = {}
        for frame_number, hits in all_hits.items():
            hit = Hit(hits, game)
            hit_objects[hit.frame_number] = hit

        # parse all_hits to rule out consecutive hits that are actually just one hit
        hit_sequences = []
        game_max_frame_number = game.frames.index.values.max()
        frame_number = 1
        while frame_number < game_max_frame_number:
            if frame_number in hit_objects:
                # start new hit sequence
                hit = hit_objects[frame_number]
                hit_sequence = [hit]
                while frame_number + 1 in hit_objects and hit_objects[frame_number + 1].player is hit.player:
                    hit_sequence.append(hit_objects[frame_number + 1])
                    frame_number += 1
                hit_sequences.append(hit_sequence)
                frame_number += 1
            else:
                frame_number += 1

        game.hits = {}
        for hit_sequence in hit_sequences:
            actual_hit = None
            actual_hit_distance = 999999
            for hit in hit_sequence:
                if hit.collision_distance < actual_hit_distance:
                    actual_hit = hit
                    actual_hit_distance = hit.collision_distance
            if actual_hit is None:
                # print('Found null hit sequence:', hit_sequence)
                continue
            game.hits[actual_hit.frame_number] = actual_hit

        return len(game.hits)

    @staticmethod
    def add_analytics_attributes(game):
        print("Found %s hits in game." % len(game.hits))

        for hit in game.hits.values():
            hit.analytics = {'pass_': False,
                             'passed': False,
                             'dribble': False,
                             'dribble_continuation': False,
                             'shot': False,
                             'assist': False,
                             'assisted': False,
                             'goal': False,
                             'save': False,
                             'distance': None,
                             'distance_to_goal': None, }

        for hit in game.hits.values():
            hit.analytics['distance_to_goal'] = hit.get_distance_to_goal()

        # find last hit by goalscorer for each goal frame
        last_goal_frame = 0
        for goal in game.goals:
            last_player_hit = None
            for hit_frame_number, hit in game.hits.items():
                # print(hit_frame_number)
                if not last_goal_frame < hit.frame_number <= goal.frame_number:
                    continue

                if hit.player is goal.player:
                    last_player_hit = hit

            goal.hit = last_player_hit
            if last_player_hit is None:
                print("Could not find hit for goal: %s" % goal)
            else:
                last_player_hit.analytics['goal'] = True
                # print("Found hit for goal: %s, %s" % (goal.frame_number, goal.hit))
                # print("Player: %s scored %s goals" % (goal.player.name, goal.player.goals))

            last_goal_frame = goal.frame_number

        # find passes and assists
        hit_frame_numbers = sorted(game.hits)
        for hit_number in range(len(hit_frame_numbers)):
            hit_frame_number = hit_frame_numbers[hit_number]
            hit = game.hits[hit_frame_number]
            previous_hit = None
            next_hit = None
            try:
                previous_hit_frame_number = hit_frame_numbers[hit_number - 1]
                if game.frames.loc[previous_hit_frame_number, 'goal_number'] == game.frames.loc[
                    hit_frame_number, 'goal_number']:
                    previous_hit = game.hits[previous_hit_frame_number]
                    hit.previous_hit = previous_hit
            except IndexError:
                pass
            try:
                next_hit_frame_number = hit_frame_numbers[hit_number + 1]
                if game.frames.loc[next_hit_frame_number, 'goal_number'] == game.frames.loc[
                    hit_frame_number, 'goal_number']:
                    next_hit = game.hits[next_hit_frame_number]
                    hit.next_hit = next_hit
            except IndexError:
                pass

            # hit distance
            if next_hit:
                displacement = next_hit.ball_data.loc['pos_x':'pos_z'].values - hit.ball_data.loc[
                                                                                'pos_x':'pos_z'].values
                hit.analytics['distance'] = np.sqrt(np.square(displacement).sum())
            elif hit.analytics['goal']:

                hit.analytics['distance'] = 0

            if next_hit:
                if hit.player is next_hit.player:
                    if not hit.analytics['dribble_continuation']:
                        hit.analytics['dribble'] = True
                    next_hit.analytics['dribble_continuation'] = True
                elif hit.player.is_orange == next_hit.player.is_orange:
                    hit.analytics['pass_'] = True
                    next_hit.analytics['passed'] = True

                    next_player_scores = False
                    next_player_goal_hit = None
                    i = 1
                    while True:
                        try:
                            _next_next_hit_frame_number = hit_frame_numbers[hit_number + i]
                            _next_next_hit = game.hits[_next_next_hit_frame_number]
                            if _next_next_hit.player is not next_hit.player:
                                break
                            if _next_next_hit.analytics['goal']:
                                next_player_scores = True
                                next_player_goal_hit = _next_next_hit
                                break
                            i += 1
                        except IndexError:
                            break

                    if next_player_scores:
                        hit.analytics['assist'] = True
                        next_player_goal_hit.analytics['assisted'] = True
                        print('Found assist (%s) for goal (%s)' % (hit, next_hit))

        # find shots
        for hit in game.hits.values():
            ball = Ball(hit.ball_data, hit.player.is_orange)
            is_shot = ball.get_is_shot()
            if is_shot:
                hit.analytics['shot'] = True
                if hit.analytics['goal']:
                    print('Found shot for goal:', hit)
            if hit.analytics['goal'] and not is_shot:
                print('Goal is not shot: %s' % hit)
            # if hit.analytics['goal']:
            #     print(is_shot)
            #     next_ball =  Ball(hit.post_hit_ball_data, hit.player.is_orange)
            #     print('next is shot', next_ball.get_is_shot())
            #     print('Goal is not shot: %s' % hit)
            #     print(hit.ball_data)
            #     ball.plot_sim_data()

    def get_distance_to_goal(self):
        _goal_x = min(max(self.ball_data['pos_x'], GOAL_X / 2), -GOAL_X / 2)
        _goal_y = -MAP_Y / 2 if self.player.is_orange else MAP_Y / 2

        displacement = self.ball_data['pos_x':'pos_y'].values - (_goal_x, _goal_y)
        distance = np.sqrt(np.square(displacement).sum())

        return distance


def test_variables(game):
    hit_counts = {}
    for i in range(70, 200, 20):
        global COLLISION_DISTANCE_LOW_LIMIT
        COLLISION_DISTANCE_LOW_LIMIT = i
        hit_count = Hit.add_hits_to_game(game)
        hit_counts[i] = hit_count
        print(i, hit_count)
    import matplotlib.pyplot as plt
    plt.plot(hit_counts.keys(), hit_counts.values(), '.')
    plt.show()


def get_average_game_hit_collision_distance(game):
    Hit.add_hits_to_game(game)

    hit_distances = [hit.collision_distance for hit in game.hits.values()]
    print(np.mean(hit_distances))


