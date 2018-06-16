import os
import subprocess
import json

from game.game import Game
# from analyser.game_analyser import analyse_game
from controls.controls import get_controls


def decompile_replay(path):
    binaries = [f for f in os.listdir('rattletrap') if not f.endswith('.py')]
    if os.name == 'nt':
        binary = [f for f in binaries if f.endswith('.exe')][0]
        os.chdir(os.path.dirname(__file__))
        output_path = f'replays/decompiled/{path.replace("replay", "json")}'
        if not os.path.isfile(output_path):
            cmd = [f'rattletrap/{binary}', '-i', f'replays/{path}', '--output',
                   output_path]
            print(cmd)
            subprocess.check_output(cmd)
        _json = json.load(open(output_path))
        game = Game(loaded_json=_json)
        get_controls(game)
        return game


if __name__ == '__main__':
    for p in [f for f in os.listdir('replays/') if os.path.isfile('replays/' + f)]:
        print(p)
        decompile_replay(p)
