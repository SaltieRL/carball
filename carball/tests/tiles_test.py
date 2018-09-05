import unittest

import numpy as np
from carball.analysis.utils.split_location import LocationSplitManager, STANDARD_MIN_VALUES, STANDARD_MAX_VALUES


class DBTest(unittest.TestCase):
    def __init__(self, *args):
        super().__init__(*args)
        self.split_manager = None

    def setUp(self):
        self.split_manager = LocationSplitManager(3, np.array([7, 7, 5]), STANDARD_MIN_VALUES, STANDARD_MAX_VALUES)

    def test_replay_attrs(self):
        result = self.split_manager.create_boxes(np.array([0, 0, 0]))
        answer = [np.array([3., 3., 0.]), np.array([3., 3., 0.]), np.array([3., 3., 0.])]
        for i in range(len(result)):
            np.testing.assert_equal(answer[i], result[i])
        print(result)


if __name__ == '__main__':
    unittest.main()



