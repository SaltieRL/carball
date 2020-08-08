import itertools
import logging
from typing import Dict

import numpy as np
import pandas as pd
from carball.generated.api.player_pb2 import Player

from carball.generated.api.stats.events_pb2 import Bump

from carball.generated.api.player_id_pb2 import PlayerId
from carball.json_parser.game import Game

from carball.generated.api import game_pb2

logger = logging.getLogger(__name__)

# Decreasing this, risks not counting bumps where one car is directly behind another (driving in the same direction).
# Increasing this, risks counting non-contact close proximity (e.g. one car cleanly jumped over another =/= bump).
PLAYER_CONTACT_DISTANCE = 200

# Needs to be relatively high to account for two cars colliding 'diagonally': /\
MAX_BUMP_ALIGN_ANGLE = 60

# Approx. half of goal height.
# (could be used to discard all aerial contact as bumps, although rarely an aerial bump WAS, indeed, intended)
AERIAL_BUMP_HEIGHT = 300


# TODO Post-bump analysis // Bump impact analysis.
# Could also try to analyse bump severity (analyse velocities?)
class BumpAnalysis:
    def __init__(self, game: Game, proto_game: game_pb2):
        self.proto_game = proto_game

    def get_bumps_from_game(self, data_frame: pd.DataFrame, player_map):
        self.create_bumps_from_demos(self.proto_game)
        self.create_bumps_from_player_proximity(data_frame, player_map)

    def create_bumps_from_demos(self, proto_game):
        for demo in proto_game.game_metadata.demos:
            self.add_bump(demo.frame_number, demo.victim_id, demo.attacker_id, True)

    def create_bumps_from_player_proximity(self, data_frame: pd.DataFrame, player_map: Dict[str, Player]):
        """
        Attempt to find all instances between each possible player combination
        where they got within PLAYER_CONTACT_DISTANCE.
        Then, add each instance to the API.

        NOTES:
        Currently, this yields more 'bumps' than there are actually.
          This is mostly due to aerial proximity, where a bump was NOT intended or no contact was made.
          This also occurs near the ground, where cars flip awkwardly past each other.
        """

        # An array of player names to get player combinations; and a dict of player names to their IDs to create bumps.
        player_names = []
        player_name_to_id = {}
        for player in player_map.values():
            player_names.append(player.name)
            player_name_to_id[player.name] = player.id

        # For each player pair combination (nCr), get all frames where they got close and then filter those as bumps.
        for player_pair in itertools.combinations(player_names, 2):
            players_close_frame_idxs = BumpAnalysis.get_players_close_frame_idxs(data_frame,
                                                                                 str(player_pair[0]),
                                                                                 str(player_pair[1]))

            if len(players_close_frame_idxs) > 0:
                likely_bumps = BumpAnalysis.filter_bumps(data_frame, player_pair, players_close_frame_idxs)
                self.add_non_demo_bumps(likely_bumps, player_name_to_id)
            else:
                logger.info("Players (" + player_pair[0] + " and " + player_pair[1] + ") did not get close "
                                                                                      "during the match.")

    def add_bump(self, frame: int, victim_id: PlayerId, attacker_id: PlayerId, is_demo: bool) -> Bump:
        """
        Add a new bump to the proto_game object.
        """
        bump = self.proto_game.game_stats.bumps.add()
        bump.frame_number = frame
        bump.attacker_id.id = attacker_id.id
        bump.victim_id.id = victim_id.id
        if is_demo:
            bump.is_demo = True

    def add_non_demo_bumps(self, likely_bumps, player_name_to_id):
        """
        Add a new bump to the proto_game object.
        This method takes an array of likely (filtered) bumps, in the following form:
            (frame_idx, attacker_name, victim_name)
        and carefully adds them to the proto_game object (i.e. check for demo duplicates).
        """

        # Get an array of demo frame idxs to compare later.
        demo_frame_idxs = []
        for demo in self.proto_game.game_metadata.demos:
            demo_frame_idxs.append(demo.frame_number)

        # For each bump tuple, if its frame index is not similar to a demo frame index, add it via add_bump().
        for likely_bump in likely_bumps:
            likely_bump_frame_idx = likely_bump[0]
            if not any(np.isclose(demo_frame_idxs, likely_bump_frame_idx, atol=10)):
                self.add_bump(likely_bump[0], player_name_to_id[likely_bump[2]], player_name_to_id[likely_bump[1]],
                              is_demo=False)

    @staticmethod
    def filter_bumps(data_frame, player_pair, players_close_frame_idxs):
        """
        Filter the frames where two players got close - the filtered frames are likely bumps.

        The main principle used is the angle between two vectors (aka 'alignment'):
            the velocity vector of player A;
            the positional vector of the difference between the positions of player B and player A.
        Both of these vectors point away from player A, and if the angle between them is small - it is likely that
        Player A bumped Player B. (Velocity going 'through' Player B's Position)

        Some further checks are done to categorise the bump (i.e. is_aerial_bump(), is_bump_velocity() )
        """
        likely_bumps = []

        # Split a list of frame indexes into intervals where indexes are within 3 of each other (i.e. consecutive).
        players_close_frame_idxs_intervals = BumpAnalysis.get_players_close_intervals(players_close_frame_idxs)

        # For each such interval, take (currently only) the first frame index and analyse car behaviour.
        for interval in players_close_frame_idxs_intervals:
            frame_before_bump = interval[0]

            # Calculate both player bump alignments (see comment at method top).
            p1_alignment_before = BumpAnalysis.get_player_bump_alignment(data_frame, frame_before_bump,
                                                                         player_pair[0], player_pair[1])
            p2_alignment_before = BumpAnalysis.get_player_bump_alignment(data_frame, frame_before_bump,
                                                                         player_pair[1], player_pair[0])

            # Determine the attacker and the victim (see method for more info). is_ambiguous signifies whether
            # the attacker-victim pair is clear or not.
            attacker, victim, is_ambiguous = BumpAnalysis.determine_attacker_victim(player_pair[0], player_pair[1],
                                                                               p1_alignment_before, p2_alignment_before)

            # Determine if the bump was above AERIAL_BUMP_HEIGHT.
            is_aerial_bump = BumpAnalysis.is_aerial_bump(data_frame, player_pair[0], player_pair[1], frame_before_bump)

            # Append the current bump data to likely bumps, if there is an attacker and a victim
            # and if it wasn't an aerial bump (most often it isn't intended, and there is often awkward behaviour).
            if attacker is not None and victim is not None and not is_aerial_bump:
                likely_bump = (frame_before_bump, attacker, victim)
                likely_bumps.append(likely_bump)

            # NOT YET IMPLEMENTED (see bottom of class):
            # BumpAnalysis.analyse_prolonged_proximity(data_frame, interval, player_pair[0], player_pair[1])

        return likely_bumps

    @staticmethod
    def get_player_bump_alignment(data_frame, frame_idx, p1_name, p2_name):
        """
        Calculate and return the angle between:
            the velocity vector of player A;
            the positional vector of the difference between the positions of player B and player A.
        """

        # Get the necessary data from the DataFrame at the given frame index.
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

        # Find the angle between the positional vector and the velocity vector.
        # NOTE: This is currently converted to DEGREES, not sure if this is bad..? ( - DivvyC)
        ang = (np.arccos(np.clip(np.dot(unit_vel1, unit_pos1), -1.0, 1.0))) * 180 / np.pi
        return ang

    @staticmethod
    def get_players_close_frame_idxs(data_frame, p1_name, p2_name):
        """
        For a pair of players, find all frame indexes where they got within PLAYER_CONTACT_DISTANCE of each other.
        Note that they did NOT necessarily make contact.
        """

        # Separate the positional data of each given player from the full DataFrame and lose the NaN value rows.
        p1_pos_df = data_frame[p1_name][['pos_x', 'pos_y', 'pos_z']].dropna(axis=0)
        p2_pos_df = data_frame[p2_name][['pos_x', 'pos_y', 'pos_z']].dropna(axis=0)

        # Calculate the vector distances between the players, and store them as a pd.Series (1D DataFrame).
        distances = (p1_pos_df.pos_x - p2_pos_df.pos_x) ** 2 + \
                    (p1_pos_df.pos_y - p2_pos_df.pos_y) ** 2 + \
                    (p1_pos_df.pos_z - p2_pos_df.pos_z) ** 2
        distances = np.sqrt(distances)

        # Only keep values < PLAYER_CONTACT_DISTANCE (see top of class).
        players_close_series = distances[distances < PLAYER_CONTACT_DISTANCE]
        # Get the frame indexes of the values (as an ndarray).
        players_close_frame_idxs = players_close_series.index.to_numpy()
        return players_close_frame_idxs

    @staticmethod
    def get_players_close_intervals(players_close_frame_idxs):
        """
        Separate a list of frame indexes into intervals with consecutive frame indexes.
        E.g. [3, 4, 5, 7, 19, 21, 23, 24, 57] is turned into [[3, 4, 5, 7], [21, 23, 24], [57]]
        """

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
            If both bump alignments are above MAX_BUMP_ALIGN_ANGLE, both values are None (no solid attacker/victim)
            If both bump alignments are within 45deg of each other, both values are None (both attackers)

        :return: A tuple in the form (Attacker, Victim, T) or (None, None, T/F), where the last bool signifies whether
        the attacker/victim are ambiguous (T) or not (F).
        """

        if BumpAnalysis.is_bump_alignment([p1_alignment, p2_alignment]):
            # if abs(p1_alignment - p2_alignment) < 45:
            #     # TODO Rework? This would indicate that the bump is ambiguous (no definite attacker/victim).
            #     return p1_name, p2_name, True
            if p1_alignment < p2_alignment:
                return p1_name, p2_name, False
            elif p2_alignment < p1_alignment:
                return p2_name, p1_name, False

        # This is ambiguous - neither player had an attacking bump angle.
        return None, None, True

    @staticmethod
    def is_aerial_bump(data_frame: pd.DataFrame, p1_name: str, p2_name: str, at_frame: int):
        """
        Check if the contact was made mid-air.
        """
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
        """
        Check if all bump alignment angles in the given list are above MAX_BUMP_ALIGN_ANGLE.
        """
        if all(abs(x) > MAX_BUMP_ALIGN_ANGLE for x in bump_angles):
            return False
        else:
            return True

    # TO SATISFY CODECOV, this is commented out for now.
    # @staticmethod
    # def analyse_prolonged_proximity(data_frame, interval, p1_name, p2_name):
    #     # TODO Redo this to do some proper analysis. Rule 1?
    #     if len(interval) > 60:
    #         print("Rule 1?")
