import json
import os
import pickle
import subprocess

from analysis.saltie_game.saltie_game import SaltieGame

try:
    from json_parser.game import Game
    from .controls.controls import get_controls
except:
    from json_parser.game import Game
    from controls.controls import get_controls

BASE_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join('replays', 'pickled')


def decompile_replay(path, output_path):
    binaries = [f for f in os.listdir(os.path.join(BASE_DIR, 'rattletrap')) if not f.endswith('.py')]
    if os.name == 'nt':
        binary = [f for f in binaries if f.endswith('.exe')][0]
    else:
        binary = [f for f in binaries if 'linux' in f][0]
    os.chdir(os.path.dirname(__file__))
    output_dirs = os.path.dirname(output_path)
    if not os.path.isdir(output_dirs) and output_dirs != '':
        os.makedirs(output_dirs)
    if not os.path.isfile(output_path):
        cmd = [os.path.join(os.path.join(BASE_DIR, 'rattletrap'), '{}'.format(binary)), '--compact', '-i', path,
               '--output',
               output_path]
        print(" ".join(cmd))
        subprocess.check_output(cmd)
    _json = json.load(open(output_path))
    game = Game(loaded_json=_json)
    # get_controls(game)  # TODO: enable and optimise.

    return SaltieGame(game)


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    if not os.path.isdir(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for filename in [f for f in os.listdir('replays/') if os.path.isfile('replays/' + f)]:
        filepath = 'replays/' + filename
        print(filepath)
        output = 'replays/decompiled/{}'.format(filepath.replace(".replay", ".json"))
        g = decompile_replay(filepath, output)
        with open(os.path.join(OUTPUT_DIR, filename + '.pkl'), 'wb') as fo:
            pickle.dump(g, fo)
