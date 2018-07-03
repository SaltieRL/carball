import os
import pickle
import subprocess
import json

from game.game import Game
# from analyser.game_analyser import analyse_game
from controls.controls import get_controls

OUTPUT_DIR = os.path.join('replays', 'pickled')
if not os.path.isdir(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


def decompile_replay(path):
    binaries = [f for f in os.listdir('rattletrap') if not f.endswith('.py')]
    if os.name == 'nt':
        binary = [f for f in binaries if f.endswith('.exe')][0]
    else:
        binary = [f for f in binaries if 'linux' in f][0]
    os.chdir(os.path.dirname(__file__))
    output_path = 'replays/decompiled/{}'.format(path.replace("replay", "json"))
    if not os.path.isdir(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))
    if not os.path.isfile(output_path):
        cmd = ['rattletrap/{}'.format(binary), '-i', 'replays/{}'.format(path), '--output',
               output_path]
        print(" ".join(cmd))
        subprocess.check_output(cmd)
    _json = json.load(open(output_path))
    game = Game(loaded_json=_json)
    get_controls(game)
    return game


if __name__ == '__main__':
    for p in [f for f in os.listdir('replays/') if os.path.isfile('replays/' + f)]:
        print(p)
        g = decompile_replay(p)
        with open(os.path.join(OUTPUT_DIR, p + '.pkl'), 'wb') as fo:
            pickle.dump(g, fo)
