import gzip
import os

from ..analysis.utils.pandas_manager import PandasManager

OUTPUT_DIR = os.path.join('..', 'replays', 'pickled')
OUTPUT_FORMAT = '.gzip'
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


class Test_Database():
    def setup_method(self):
        self.pandas = None
        if not os.path.isdir(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)

        for filename in [f for f in os.listdir(OUTPUT_DIR) if os.path.isfile(os.path.join(OUTPUT_DIR, f))]:
            if OUTPUT_FORMAT in filename:
                filepath = os.path.join(OUTPUT_DIR, filename)
                with gzip.open(filepath, 'rb') as file:
                    self.pandas = PandasManager.read_numpy_from_memory(file)

    def test_replay_attrs(self):
        if self.pandas is not None:
            print(self.pandas)
