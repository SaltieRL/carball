import numpy as np
import pandas as pd
from carball.generated.api import game_pb2
from carball.analysis.constants.field_constants import FieldConstants


class PickupAnalysis:
    field_constants = FieldConstants()
    BIG_BOOST_POSITIONS = field_constants.get_big_pads()
    SMALL_BOOST_POSITIONS = field_constants.get_small_pads()
    BIG_BOOST_RADIUS = 208
    SMALL_BOOST_RADIUS = 149  # 144 doesn't work for some pickups that are very close to the edge.
    BIG_BOOST_HEIGHT = 168
    SMALL_BOOST_HEIGHT = 165
    # Choosing how many frames to be open to setting a pickup. Back is for when the player is ahead of the server (usually smaller)
    LAG_BACK = 6
    LAG_FORWARD = 14

    @classmethod
    def add_pickups(cls, proto_game: game_pb2.Game, data_frame: pd.DataFrame):

        for player in proto_game.players:
            player_vals_df = data_frame[player.name][['pos_x', 'pos_y', 'pos_z', 'boost']].copy()
            player_vals_df['boost'] /= 2.55
            player_vals_df['boost'] = player_vals_df['boost'].round(5)
            player_vals_df = player_vals_df.dropna(axis=0, how='all')
            player_vals_df = player_vals_df.fillna(0)
            player_vals_df['boost_collect'] = cls.get_boost_collect(player_vals_df)
            data_frame[player.name, 'boost_collect'] = player_vals_df['boost_collect']
        return

    @classmethod
    def get_boost_collect(cls, player_vals_df):
        # Get a series with indexes as a subset of the indexes of df, values being pad label picked up.
        # Iterate through every pad, label each frame in the path with which boost pad it was in range of.
        df = player_vals_df.copy()
        path = df.drop(['pos_z', 'boost'], axis=1)
        big_labels = np.zeros(len(path))
        small_labels = np.zeros(len(path))
        # Calculate the distances from each pad. Add label of the pad if distance <= radius
        for pad in cls.BIG_BOOST_POSITIONS:
            distances = np.sqrt(np.square(path.values - pad[:2]).sum(axis=1, dtype=np.float32))
            big_labels += (pad[2] * (distances <= cls.BIG_BOOST_RADIUS))

        for pad in cls.SMALL_BOOST_POSITIONS:
            distances = np.sqrt(np.square(path.values - pad[:2]).sum(axis=1, dtype=np.float32))
            small_labels += (pad[2] * (distances <= cls.SMALL_BOOST_RADIUS))
        # Add labels and exclude labels with z too high. Didn't calculate this earlier because its a flat height)
        df['pad_in_range'] = 0
        df['pad_in_range'] += small_labels
        df.loc[df['pos_z'] >= cls.SMALL_BOOST_HEIGHT, 'pad_in_range'] = 0
        df['pad_in_range'] += big_labels
        df.loc[df['pos_z'] >= cls.BIG_BOOST_HEIGHT, 'pad_in_range'] = 0
        # Get the gains in boost per frame
        df['gains'] = df['boost'].diff().clip(0)
        # Get whether we entered or exited the range of a pad per frame
        df['status_change'] = (df['pad_in_range'].diff(1))
        df = df.fillna(0)
        # Get the index of the frame we most recently entered a pad range, per frame.
        df['recent_entry_index'] = df.index
        df.loc[df['status_change'] <= 0, 'recent_entry_index'] = 0
        df['recent_entry_index'] = df['recent_entry_index'].replace(0, np.nan).fillna(
            method='bfill', limit=cls.LAG_BACK).fillna(
            method='ffill', limit=cls.LAG_FORWARD)
        gains_frames = df.loc[
            ((df['gains'] > 5) & (df['boost'] != 33.33333)) | ((df['gains'] > 0) & (df['boost'] > 95.0))].copy()

        gains_indexes = gains_frames['recent_entry_index'].dropna()

        pickups = df.loc[gains_indexes]['status_change'].copy()
        pickups = pickups.loc[~pickups.index.duplicated(keep='first')]
        return pickups
