import numpy as np


FULL_BOOST_POSITIONS = np.array([
    (3000, -4100),
    (-3000, -4100),
    (3000, 0),
    (-3000, 0),
    (3000, 4100),
    (-3000, 4100),
])


def get_if_full_boost_position(position: np.array) -> bool:
    # returns 1 for full boost, 0 for small boost
    if len(position) > 2:
        position = position[0:2]

    distances_from_boosts = np.sqrt(np.square(FULL_BOOST_POSITIONS - position.values).sum(axis=1, dtype=np.float32))
    allowed_distance_from_boost = 800
    if np.any(distances_from_boosts < allowed_distance_from_boost):
        return True
    else:
        return False
