import os
import unittest

from carball import decompile_replays

OUTPUT_DIR = os.path.join('..', 'replays', 'pickled')
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


class DBTest(unittest.TestCase):
    def setUp(self):
        if not os.path.isdir(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)

        replays_folder = os.path.join(BASE_DIR, 'replays')
        for filename in [f for f in os.listdir(replays_folder) if os.path.isfile(os.path.join(replays_folder, f))]:
            filepath = 'replays/' + filename
            print(filepath)
            output = 'replays/decompiled/{}'.format(filepath.replace(".replay", ".json"))
            self.g = decompile_replays.decompile_replay(filepath, output)
            break

    def test_replay_attrs(self):
        self.assertIsNotNone(self.g.api_game.name)
        self.assertIsNotNone(self.g.api_game.map)
        self.assertIsNotNone(self.g.api_game.id)


if __name__ == '__main__':
    unittest.main()
