import numpy as np
from ..analysis.utils.split_location import LocationSplitManager, STANDARD_MIN_VALUES, STANDARD_MAX_VALUES


class Test_TileCreation():

    def test_location_split(self):
        split_manager = LocationSplitManager(3, np.array([7, 7, 5]), STANDARD_MIN_VALUES, STANDARD_MAX_VALUES)
        result = split_manager.create_boxes(np.array([0, 0, 0]))
        answer = [np.array([3., 3., 0.]), np.array([3., 3., 0.]), np.array([3., 3., 0.])]
        for i in range(len(result)):
            np.testing.assert_equal(answer[i], result[i])
        print(result)
