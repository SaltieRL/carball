import gzip
import json
import os
import subprocess
import traceback
import logging

from replay_analysis.analysis.analysis_manager import AnalysisManager

logger = logging.getLogger(__name__)

from replay_analysis.json_parser.game import Game
from replay_analysis.controls.controls import get_controls
from json_parser.sanity_check import sanity_check

BASE_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join('replays', 'pickled')


def decompile_replay(path, output_path):
    binaries = [f for f in os.listdir(os.path.join(BASE_DIR, 'rattletrap')) if not f.endswith('.py')]
    if os.name == 'nt':
        binary = [f for f in binaries if f.endswith('.exe')][0]
    else:
        binary = [f for f in binaries if 'linux' in f][0]
    try:
        os.chdir(os.path.dirname(__file__))
    except:
        logger.warning("Unable to change directory path")
    output_dirs = os.path.dirname(output_path)
    if not os.path.isdir(output_dirs) and output_dirs != '':
        os.makedirs(output_dirs)
    if not os.path.isfile(output_path):
        cmd = [os.path.join(os.path.join(BASE_DIR, 'rattletrap'), '{}'.format(binary)), '--compact', '-i', path,
               '--output',
               output_path]
        print(" ".join(cmd))
        subprocess.check_output(cmd)
    print(output_path)
    _json = json.load(open(output_path, encoding="utf8"))
    game = Game(loaded_json=_json)
    # get_controls(game)  # TODO: enable and optimise.
    sanity_check.check_game(game)
    analysis = AnalysisManager(game)
    analysis.create_analysis()

    return analysis


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    success = 0
    failure = 0
    if not os.path.isdir(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for filename in [f for f in os.listdir('replays/') if os.path.isfile('replays/' + f)]:
        filepath = 'replays/' + filename
        print(filepath)
        output = 'replays/decompiled/{}'.format(filepath.replace(".replay", ".json"))
        try:
            analysis_manager = decompile_replay(filepath, output)
            with open(os.path.join(OUTPUT_DIR, filename + '.pts'), 'wb') as fo:
                analysis_manager.write_proto_out_to_file(fo)
            with gzip.open(os.path.join(OUTPUT_DIR, filename + '.gzip'), 'wb') as fo:
                analysis_manager.write_pandas_out_to_file(fo)
                success += 1
        except Exception as e:
            traceback.print_exc()
            failure += 1
    ratio = success / float(success + failure)
    print('success ratio:', ratio)
