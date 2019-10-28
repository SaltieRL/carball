import numpy as np

BIG_RADIUS = 208
SMALL_RADIUS = 144
BIG_HEIGHT = 168
SMALL_HEIGHT = 165
BIG_SQUARE_RADIUS = 160
SMALL_SQUARE_RADIUS = 96
SQUARE_HEIGHT = 140
# The first two values are X,Y. The last value is (RLBot_label +1) and multiplied by 10 if its a bigboost.
# Bigboosts are *10 so that all big boost values are larger than all small boost values, for easy querying.
# If nobody needs these to be RLBot labels, this can be simplified.
BIG_BOOST_POSITIONS = np.array([
    (3072.0, -4096.0, 50),
    (-3072.0, -4096.0, 40),
    (3584.0, 0.0, 190),
    (-3584.0, 0.0, 160),
    (3072.0, 4096.0, 300),
    (-3072.0, 4096.0, 310)
])
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


def get_if_full_boost_position(position: np.array) -> bool:
    # returns 1 for full boost, 0 for small boost
    if len(position) > 2:
        position = position[0:2]

    distances_from_boosts = np.sqrt(np.square(BIG_BOOST_POSITIONS - position.values).sum(axis=1, dtype=np.float32))
    allowed_distance_from_boost = 800
    if np.any(distances_from_boosts < allowed_distance_from_boost):
        return True
    else:
        return False
