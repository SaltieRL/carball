import os
import unittest

from carball.analysis.analysis_manager import AnalysisManager
from carball.tests import utils
from carball.tests.utils import get_replay_list
from .. import decompile_replays

OUTPUT_DIR = os.path.join('..', 'replays', 'pickled')
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


class DBTest(unittest.TestCase):
    def setUp(self):
        if not os.path.isdir(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)

        replays_folder = os.path.join(BASE_DIR, 'replays')
        if not os.path.isdir(replays_folder):
            os.makedirs(replays_folder)
        downloaded_list = []
        for filename in get_replay_list():
            replay = utils.download_replay_discord(filename)
            filename = utils.save_locally(replay)
            downloaded_list.append(filename)
        files = [os.path.join(replays_folder, f) for f in os.listdir(replays_folder) if
                 os.path.isfile(os.path.join(replays_folder, f))] + downloaded_list

        for filename in files:
            print(filename)
            output = 'replays/decompiled/{}'.format(os.path.basename(filename).replace(".replay", ".json"))
            self.g: AnalysisManager = decompile_replays.analyze_replay_file(filename, output)
            break

    def test_replay_attrs(self):
        self.assertIsNotNone(self.g.protobuf_game.game_metadata.match_guid)
        self.assertIsNotNone(self.g.protobuf_game.game_metadata.map)
        self.assertIsNotNone(self.g.protobuf_game.game_metadata.id)


if __name__ == '__main__':
    unittest.main()
