import numpy as np


# BOOST_POSITION_TYPE = {
#     {'pos_x': 3000, 'pos_y': -4100, 'type': 1},
#     {'pos_x': -3000, 'pos_y': -4100, 'type': 1},
#     {'pos_x': 3000, 'pos_y': 0, 'type': 1},
#     {'pos_x': -3000, 'pos_y': 0, 'type': 1},
#     {'pos_x': 3000, 'pos_y': 4100, 'type': 1},
#     {'pos_x': -3000, 'pos_y': 4100, 'type': 1},
# }

FULL_BOOST_POSITIONS = np.array([
    (3000, -4100),
    (-3000, -4100),
    (3000, 0),
    (-3000, 0),
    (3000, 4100),
    (-3000, 4100),
])


def get_boost_type_from_position(position):
    if len(position) > 2:
        position = position[0:2]

    distances_from_boosts = np.sqrt(np.square(FULL_BOOST_POSITIONS - position.values).sum(axis=1, dtype=np.float32))
    allowed_distance_from_boost = 800
    if np.any(distances_from_boosts < allowed_distance_from_boost):
        return 1
    else:
        return 0


