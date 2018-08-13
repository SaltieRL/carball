import os
import unittest

from .. import decompile_replays

OUTPUT_DIR = os.path.join('..', 'replays', 'pickled')


class DBTest(unittest.TestCase):
    def setUp(self):
        if not os.path.isdir(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        for filename in [f for f in os.listdir('replays/') if os.path.isfile('replays/' + f)]:
            filepath = 'replays/' + filename
            print(filepath)
            output = 'replays/decompiled/{}'.format(filepath.replace(".replay", ".json"))
            self.g = decompile_replays.decompile_replay(filepath, output)
            break

    def test_replay_attrs(self):
        print (self.g.api_game.name)
        print (self.g.api_game.map_)
        print (self.g.api_game.replay_id)


if __name__ == '__main__':
    unittest.main()
