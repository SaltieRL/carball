import numpy as np


STANDARD_SIZE = np.array([4096 * 2, 5120 * 2, 2044])
STANDARD_MIN_VALUES = np.array([-4096, -5120, 0])
STANDARD_MAX_VALUES = np.array([4096, 5120, 2000])


class LocationSplitManager:
    def __init__(self, num_layers, layer_grid_sizes, min_values, max_values):
        """
        Creates a location split manager
        :param num_layers: Number of layers for this grid.
        :param layer_grid_sizes:
        :param total_size:
        """
        self.min_values = min_values
        self.max_values = max_values
        self.layer_grid_sizes = layer_grid_sizes
        self.num_layers = num_layers
        self.total_size = max_values - min_values

    def create_boxes(self, position):
        output_tiles = []
        for i in range(self.num_layers):
            layer_mult = (1 + i)
            max_layer_value = (self.layer_grid_sizes ** layer_mult)
            raw_scaled_position = ((position - self.min_values) /
                                   self.total_size) * max_layer_value
            print(raw_scaled_position)
            full_position = np.floor(np.maximum(0, np.minimum(raw_scaled_position, max_layer_value - 1)))

            output_tiles.append(full_position % self.layer_grid_sizes)
        return output_tiles
