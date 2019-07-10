import logging

import numpy as np

from .car import read_xl

logger = logging.getLogger(__name__)


class Hitbox:
    xl = read_xl()

    def __init__(self, car_item_id: int):
        column_names = ['Length', 'Width', 'Height', 'Offset', 'Elevation']
        try:
            car_hitbox = self.xl.loc[car_item_id, column_names].values
        except KeyError:
            logger.debug("Cannot find car body id: %s. Falling back onto Octane." % car_item_id)
            car_hitbox = self.xl.loc[23, column_names].values

        self.car_length, self.car_width, self.car_height, self.car_offset, self.car_elevation = car_hitbox
        self.car_x_lims = (-self.car_length / 2 + self.car_offset,
                           self.car_length / 2 + self.car_offset)
        self.car_y_lims = (-self.car_width / 2,
                           self.car_width / 2)
        self.car_z_lims = (-self.car_height / 2 + self.car_elevation,
                           self.car_height / 2 + self.car_elevation)

    def get_collision_distance(self, ball_displacement) -> np.float64:
        if np.isnan(ball_displacement).any():
            return np.nan
        pos_x, pos_y, pos_z = ball_displacement
        # x axis
        if pos_x < self.car_x_lims[0]:
            x_dist = abs(self.car_x_lims[0] - pos_x)
        elif pos_x > self.car_x_lims[1]:
            x_dist = abs(self.car_x_lims[1] - pos_x)
        else:
            x_dist = 0
        # y axis
        if pos_y < self.car_y_lims[0]:
            y_dist = abs(self.car_y_lims[0] - pos_y)
        elif pos_y > self.car_y_lims[1]:
            y_dist = abs(self.car_y_lims[1] - pos_y)
        else:
            y_dist = 0
        # z axis
        if pos_z < self.car_z_lims[0]:
            z_dist = abs(self.car_z_lims[0] - pos_z)
        elif pos_z > self.car_z_lims[1]:
            z_dist = abs(self.car_z_lims[1] - pos_z)
        else:
            z_dist = 0

        return (x_dist ** 2 + y_dist ** 2 + z_dist ** 2) ** 0.5
