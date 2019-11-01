import numpy as np
import pandas as pd
from carball.generated.api import game_pb2

# The first two values are X,Y. The last value is (RLBot_label +1) and multiplied by 10 if its a bigboost.
# Bigboosts are *10 so that all big boost values are larger than all small boost values, for easy querying.
# If nobody needs these to be RLBot labels, this can be simplified.
BIG_BOOST_POSITIONS = np.array([
    (3072, -4096, 50),
    (-3072, -4096, 40),
    (3584, 0, 190),
    (-3584, 0, 160),
    (3072, 4096, 300),
    (-3072, 4096, 310)])

SMALL_BOOST_POSITIONS = np.array([
    (0.0, -4240.0, 1),
    (-1792.0, -4184.0, 2),
    (1792.0, -4184.0, 3),
    (- 940.0, -3308.0, 6),
    (940.0, -3308.0, 7),
    (0.0, -2816.0, 8),
    (-3584.0, -2484.0, 9),
    (3584.0, -2484.0, 10),
    (-1788.0, -2300.0, 11),
    (1788.0, -2300.0, 12),
    (-2048.0, -1036.0, 13),
    (0.0, -1024.0, 14),
    (2048.0, -1036.0, 15),
    (-1024.0, 0.0, 17),
    (1024.0, 0.0, 18),
    (-2048.0, 1036.0, 20),
    (0.0, 1024.0, 21),
    (2048.0, 1036.0, 22),
    (-1788.0, 2300.0, 23),
    (1788.0, 2300.0, 24),
    (-3584.0, 2484.0, 25),
    (3584.0, 2484.0, 26),
    (0.0, 2816.0, 27),
    (- 940.0, 3310.0, 28),
    (940.0, 3308.0, 29),
    (-1792.0, 4184.0, 32),
    (1792.0, 4184.0, 33),
    (0.0, 4240.0, 34)
])

BIG_BOOST_RADIUS = 208
SMALL_BOOST_RADIUS = 149  # 144 doesn't work for some pickups that are very close to the edge.
BIG_BOOST_HEIGHT = 168
SMALL_BOOST_HEIGHT = 165
# Choosing how many frames to be open to setting a pickup. Back is for when the player is ahead of the server (usually smaller)
LAG_BACK = 6
LAG_FORWARD = 14

BOOST_POSITIONS = np.concatenate((BIG_BOOST_POSITIONS, SMALL_BOOST_POSITIONS))


class PickupAnalysis:

    @staticmethod
    def add_pickups(proto_game: game_pb2.Game, data_frame: pd.DataFrame):

        for player in proto_game.players:
            player_vals_df = data_frame[player.name][['pos_x', 'pos_y', 'pos_z', 'boost']].copy()
            player_vals_df['boost'] /= 2.55
            player_vals_df['boost'] = player_vals_df['boost'].round(5)
            player_vals_df = player_vals_df.dropna(axis=0, how='all')
            player_vals_df = player_vals_df.fillna(0)
            player_vals_df['boost_collect'] = get_boost_collect(player_vals_df)
            data_frame[player.name, 'boost_collect'] = player_vals_df['boost_collect']
        return

    @staticmethod
    def something(proto_game: game_pb2.Game, data_frame: pd.DataFrame):
        pass


def get_boost_collect(player_vals_df):
    # Get a series with indexes as a subset of the indexes of df, values being pad label picked up.
    # Iterate through every pad, label each frame in the path with which boost pad it was in range of.
    df = player_vals_df.copy()
    path = df.drop(['pos_z', 'boost'], axis=1)
    big_labels = np.zeros(len(path))
    small_labels = np.zeros(len(path))
    # Calculate the distances from each pad. Add label of the pad if distance <= radius
    for pad in BIG_BOOST_POSITIONS:
        distances = np.sqrt(np.square(path.values - pad[:2]).sum(axis=1, dtype=np.float32))
        big_labels += (pad[2] * (distances <= BIG_BOOST_RADIUS))

    for pad in SMALL_BOOST_POSITIONS:
        distances = np.sqrt(np.square(path.values - pad[:2]).sum(axis=1, dtype=np.float32))
        small_labels += (pad[2] * (distances <= SMALL_BOOST_RADIUS))
    # Add labels and exclude labels with z too high. Didn't calculate this earlier because its a flat height)
    df['pad_in_range'] = 0
    df['pad_in_range'] += small_labels
    df.loc[df['pos_z'] >= SMALL_BOOST_HEIGHT, 'pad_in_range'] = 0
    df['pad_in_range'] += big_labels
    df.loc[df['pos_z'] >= BIG_BOOST_HEIGHT, 'pad_in_range'] = 0
    # Get the gains in boost per frame
    df['gains'] = df['boost'].diff().clip(0)
    # Get whether we entered or exited the range of a pad per frame
    df['status_change'] = (df['pad_in_range'].diff(1))
    df = df.fillna(0)
    # Get the index of the frame we most recently entered a pad range, per frame.
    df['recent_entry_index'] = df.index
    df.loc[df['status_change'] <= 0, 'recent_entry_index'] = 0
    df['recent_entry_index'] = df['recent_entry_index'].replace(0, np.nan).fillna(
        method='bfill', limit=LAG_BACK).fillna(
        method='ffill', limit=LAG_FORWARD)
    gains_frames = df.loc[
        ((df['gains'] > 5) & (df['boost'] != 33.33333)) | ((df['gains'] > 0) & (df['boost'] > 95.0))].copy()

    gains_indexes = gains_frames['recent_entry_index'].dropna()

    pickups = df.loc[gains_indexes]['status_change'].copy()
    pickups = pickups.loc[~pickups.index.duplicated(keep='first')]
    return pickups
