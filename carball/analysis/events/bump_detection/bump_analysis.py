import itertools
import logging
import numpy as np
import pandas as pd
from carball.generated.api.stats.events_pb2 import Bump

from carball.generated.api.player_id_pb2 import PlayerId
from carball.json_parser.game import Game

from carball.generated.api import game_pb2

logger = logging.getLogger(__name__)

# If you decrease this, you risk not counting bumps where one car is directly behind another (driving in the same direction).
# If you increase this, you risk counting non-contact close proximity (e.g. one car cleanly jumped over another =/= bump).
PLAYER_CONTACT_MAX_DISTANCE = 200

# Needs to be relatively high to account for two cars colliding 'diagonally': /\
MAX_BUMP_ALIGN_ANGLE = 60

# Currently arbitrary:
MIN_BUMP_VELOCITY = 5000

# Approx. half of goal height.
# (could be used to discard all aerial contact as bumps, although rarely an aerial bump WAS, indeed, intended)
AERIAL_BUMP_HEIGHT = 300

# TODO Analyse the impact of bumps. (e.g. look at proximity to the ball/net)
class BumpAnalysis:
    def __init__(self, game: Game, proto_game: game_pb2):
        self.proto_game = proto_game

    def get_bumps_from_game(self, data_frame: pd.DataFrame, player_map):
        self.create_bumps_from_demos(self.proto_game)
        self.create_bumps_from_player_contact(data_frame, player_map)

    def create_bumps_from_demos(self, proto_game):
        for demo in proto_game.game_metadata.demos:
            self.add_bump(demo.frame_number, demo.victim_id, demo.attacker_id, True)

    def add_bump(self, frame: int, victim_id: PlayerId, attacker_id: PlayerId, is_demo: bool) -> Bump:
        bump = self.proto_game.game_stats.bumps.add()
        bump.frame_number = frame
        bump.attacker_id.id = attacker_id.id
        bump.victim_id.id = victim_id.id
        if is_demo:
            bump.is_demo = True

    def create_bumps_from_player_contact(self, data_frame, player_map):
        # NOTES:
        # Currently, this yields more 'bumps' than there are actually.
        #   This is mostly due to aerial proximity, where a bump was NOT intended or no contact was made.
        #   This also occurs near the ground, where cars flip awkwardly past each other.

        # POSSIBLE SOLUTIONS:
        #   Account for car hitboxes and/or rotations when calculating close proximity intervals.
        #   Do some post-bump analysis and see if car velocities aligned (i.e. analyse end of interval bump alignments)

        # Get an array of player names to use for player combinations.
        player_names = []
        for player in player_map.values():
            player_names.append(player.name)

        # For each player pair combination, get possible contact distances.
        for player_pair in itertools.combinations(player_names, 2):
            # Get all frame idxs where players were within PLAYER_CONTACT_MAX_DISTANCE.
            players_close_frame_idxs = BumpAnalysis.get_players_close_frame_idxs(data_frame,
                                                                                 str(player_pair[0]),
                                                                                 str(player_pair[1]))

            if len(players_close_frame_idxs) > 0:
                BumpAnalysis.analyse_bumps(data_frame, player_pair, players_close_frame_idxs)
            else:
                logger.info("Players (" + player_pair[0] + " and " + player_pair[1] + ") did not get close "
                                                                                      "during the match.")

    @staticmethod
    def analyse_bumps(data_frame, player_pair, players_close_frame_idxs):
        # Get all individual intervals where a player pair got close to each other.
        players_close_frame_idxs_intervals = BumpAnalysis.get_players_close_intervals(players_close_frame_idxs)

        # For each such interval, take (currently only) the beginning and analyse car behaviour.
        for interval in players_close_frame_idxs_intervals:
            frame_before_bump = interval[0]

            # Calculate alignments (angle between position vector and velocity vector, with regard to each player)
            p1_alignment_before = BumpAnalysis.get_player_bump_alignment(data_frame, frame_before_bump,
                                                                         player_pair[0], player_pair[1])
            p2_alignment_before = BumpAnalysis.get_player_bump_alignment(data_frame, frame_before_bump,
                                                                         player_pair[1], player_pair[0])
            # TODO Create Bump objects and add them to the API.
            # Determine the attacker and the victim (if alignment is below MAX_BUMP_ALIGN_ANGLE, it's the attacker)
            attacker, victim = BumpAnalysis.determine_attacker_victim(player_pair[0], player_pair[1],
                                                                      p1_alignment_before, p2_alignment_before)

            # Determine if the bump was above AERIAL_BUMP_HEIGHT.
            is_aerial_bump = BumpAnalysis.is_aerial_bump(data_frame, player_pair[0], player_pair[1], frame_before_bump)

            # Check if interval is quite long - players may be in rule 1 :) or might be a scramble.
            BumpAnalysis.analyse_prolonged_proximity(data_frame, interval, player_pair[0], player_pair[1])

    @staticmethod
    def get_player_bump_alignment(data_frame, frame_idx, p1_name, p2_name):
        p1_vel_df = data_frame[p1_name][['vel_x', 'vel_y', 'vel_z']].loc[frame_idx]
        p1_pos_df = data_frame[p1_name][['pos_x', 'pos_y', 'pos_z']].loc[frame_idx]
        p2_pos_df = data_frame[p2_name][['pos_x', 'pos_y', 'pos_z']].loc[frame_idx]

        # Get the distance vector, directed from p1 to p2.
        # Then, convert it to a unit vector.
        pos1_df = p2_pos_df - p1_pos_df
        pos1 = [pos1_df.pos_x, pos1_df.pos_y, pos1_df.pos_y]
        unit_pos1 = pos1 / np.linalg.norm(pos1)

        # Get the velocity vector of p1.
        # Then, convert it to a unit vector.
        vel1 = [p1_vel_df.vel_x, p1_vel_df.vel_y, p1_vel_df.vel_z]
        unit_vel1 = vel1 / np.linalg.norm(vel1)

        # Find the angle between the position vector and the velocity vector.
        # If this is relatively aligned - p1 probably significantly bumped p2.
        ang = (np.arccos(np.clip(np.dot(unit_vel1, unit_pos1), -1.0, 1.0))) * 180 / np.pi
        # print(p1_name + "'s bump angle=" + str(ang))
        return ang

    @staticmethod
    def get_players_close_frame_idxs(data_frame, p1_name, p2_name):
        p1_pos_df = data_frame[p1_name][['pos_x', 'pos_y', 'pos_z']].dropna(axis=0)
        p2_pos_df = data_frame[p2_name][['pos_x', 'pos_y', 'pos_z']].dropna(axis=0)

        # Calculate the vector distances between the players.
        distances = (p1_pos_df.pos_x - p2_pos_df.pos_x) ** 2 + \
                    (p1_pos_df.pos_y - p2_pos_df.pos_y) ** 2 + \
                    (p1_pos_df.pos_z - p2_pos_df.pos_z) ** 2
        distances = np.sqrt(distances)
        # Only keep values < PLAYER_CONTACT_MAX_DISTANCE (see top of class).
        players_close_series = distances[distances < PLAYER_CONTACT_MAX_DISTANCE]
        # Get the frame indexes of the values (as ndarray).
        players_close_frame_idxs = players_close_series.index.to_numpy()
        return players_close_frame_idxs

    @staticmethod
    def get_players_close_intervals(players_close_frame_idxs):
        # Find continuous intervals of close proximity, and group them together.
        all_intervals = []
        interval = []
        for index, frame_idx in enumerate(players_close_frame_idxs):
            diffs = np.diff(players_close_frame_idxs)
            interval.append(frame_idx)
            if index >= len(diffs) or diffs[index] >= 3:
                all_intervals.append(interval)
                interval = []
        return all_intervals

    @staticmethod
    def determine_attacker_victim(p1_name, p2_name, p1_alignment, p2_alignment):
        """
        Try to 'guesstimate' the attacker and the victim by comparing bump alignment angles.
            If both alignments are within 45deg, then both players were going relatively towards each other.

        :return: (Attacker, Victim)
        """

        if p1_alignment < MAX_BUMP_ALIGN_ANGLE or p2_alignment < MAX_BUMP_ALIGN_ANGLE:
            if abs(p1_alignment - p2_alignment) < 45:
                return None, None
            elif p1_alignment < p2_alignment:
                return p1_name, p2_name
            elif p2_alignment < p1_alignment:
                return p2_name, p1_name

        return None, None

    @staticmethod
    def analyse_prolonged_proximity(data_frame, interval, p1_name, p2_name):
        # TODO Redo this to do some proper analysis.
        if len(interval) > 10:
            print(" > Scramble between " + p1_name + " and " + p2_name)
        # NOTE: Could try analysing immediate post-bump effects.
        # elif len(interval) >= 5:
        #     frame_after_bump = interval[len(interval) - 1]
        #     p1_alignment_after = BumpAnalysis.get_player_bump_alignment(data_frame, frame_after_bump,
        #                                                                 p1_name, p2_name)
        #     p2_alignment_after = BumpAnalysis.get_player_bump_alignment(data_frame, frame_after_bump,
        #                                                                 p2_name, p1_name)

    @staticmethod
    def is_aerial_bump(data_frame: pd.DataFrame, p1_name: str, p2_name: str, at_frame: int):
        p1_pos_z = data_frame[p1_name].pos_z.loc[at_frame]
        p2_pos_z = data_frame[p2_name].pos_z.loc[at_frame]
        if all(x > AERIAL_BUMP_HEIGHT for x in [p1_pos_z, p2_pos_z]):
            # if all(abs(y) > 5080 for y in [p1_pos_y, p2_pos_y]):
            #     print("Backboard bump?")
            return True
        else:
            return False

    @staticmethod
    def is_bump_alignment(bump_angles):
        # Check if all bump alignment angles in the first half of the interval are above MAX_BUMP_ALIGN_ANGLE.
        if all(x > MAX_BUMP_ALIGN_ANGLE for x in bump_angles):
            return False
        else:
            return True

    @staticmethod
    def is_bump_velocity(data_frame: pd.DataFrame, p1_name: str, p2_name: str, at_frame: int):
        p1_vel_mag = np.sqrt(data_frame[p1_name].vel_x.loc[at_frame] ** 2 +
                             data_frame[p1_name].vel_y.loc[at_frame] ** 2 +
                             data_frame[p1_name].vel_z.loc[at_frame] ** 2)
        p2_vel_mag = np.sqrt(data_frame[p2_name].vel_x.loc[at_frame] ** 2 +
                             data_frame[p2_name].vel_y.loc[at_frame] ** 2 +
                             data_frame[p2_name].vel_z.loc[at_frame] ** 2)
        # Check if initial player velocities are below MIN_BUMP_VELOCITY.
        if all(x < MIN_BUMP_VELOCITY for x in [p1_vel_mag, p2_vel_mag]):
            return False
        else:
            return True
