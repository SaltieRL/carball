import gzip
import os
import unittest

from carball.analysis.utils.pandas_manager import PandasManager

OUTPUT_DIR = os.path.join('..', 'replays', 'pickled')
OUTPUT_FORMAT = '.gzip'
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


class DBTest(unittest.TestCase):
    def setUp(self):
        if not os.path.isdir(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)

        for filename in [f for f in os.listdir(OUTPUT_DIR) if os.path.isfile(os.path.join(OUTPUT_DIR, f))]:
            if OUTPUT_FORMAT in filename:
                filepath = os.path.join(OUTPUT_DIR, filename)
                with gzip.open(filepath, 'rb') as file:
                    self.pandas = PandasManager.read_numpy_from_memory(file)


    def test_replay_attrs(self):
        print(self.pandas)


if __name__ == '__main__':
    unittest.main()
