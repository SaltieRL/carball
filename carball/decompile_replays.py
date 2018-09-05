import gzip
import json
import os
import shutil
import subprocess
import traceback
import logging
import sys
import platform as pt

from google.protobuf.json_format import MessageToJson

from carball.json_parser.sanity_check.errors.errors import CheckErrorLevel

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from carball.analysis.analysis_manager import AnalysisManager

logger = logging.getLogger(__name__)

from carball.json_parser.game import Game
from carball.controls.controls import get_controls
from carball.json_parser.sanity_check import sanity_check

BASE_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join('replays', 'pickled')


def decompile_replay(replay_path, output_path):
    binaries = [f for f in os.listdir(os.path.join(BASE_DIR, 'rattletrap')) if not f.endswith('.py')]
    platform = pt.system()
    if platform == 'Windows':
        binary = [f for f in binaries if f.endswith('.exe')][0]
    elif platform == 'Linux':
        binary = [f for f in binaries if 'linux' in f][0]
    elif platform == 'Darwin':
        binary = [f for f in binaries if 'osx' in f][0]
    else:
        raise Exception('Unknown platform, unable to process replay file.')
    output_dirs = os.path.dirname(output_path)
    if not os.path.isdir(output_dirs) and output_dirs != '':
        os.makedirs(output_dirs)
    if not os.path.isfile(output_path):
        cmd = [os.path.join(os.path.join(BASE_DIR, 'rattletrap'), '{}'.format(binary)), '--compact', '-i',
               replay_path,
               '--output',
               output_path]
        logger.debug(" ".join(cmd))
        subprocess.check_output(cmd)
    logger.debug(output_path)
    _json = json.load(open(output_path, encoding="utf8"))
    game = Game(loaded_json=_json)
    # get_controls(game)  # TODO: enable and optimise.
    sanity_check.check_game(game, failing_level=CheckErrorLevel.CRITICAL)
    analysis = AnalysisManager(game)
    analysis.create_analysis()

    return analysis


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger(__name__)
    MOVE_WORKING = True
    DEBUGGING = True
    success = 0
    failure = 0
    if not os.path.isdir(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for filename in [f for f in os.listdir('replays/') if os.path.isfile('replays/' + f)]:
        filepath = 'replays/' + filename
        print(filepath)
        output = 'replays/decompiled/{}'.format(filepath.replace(".replay", ".json"))
        if DEBUGGING:
            try:
                analysis_manager = decompile_replay(filepath, output)
                with open('game.json', 'w') as f:
                    f.write(MessageToJson(analysis_manager.protobuf_game))
            except subprocess.CalledProcessError as e:
                traceback.print_exc()
        else:
            try:
                analysis_manager = decompile_replay(filepath, output)
                with open(os.path.join(OUTPUT_DIR, filename + '.pts'), 'wb') as fo:
                    analysis_manager.write_proto_out_to_file(fo)
                with gzip.open(os.path.join(OUTPUT_DIR, filename + '.gzip'), 'wb') as fo:
                    analysis_manager.write_pandas_out_to_file(fo)
                if MOVE_WORKING:
                    shutil.move(filepath, os.path.join('replays', 'working', filename))
                success += 1
            except Exception as e:
                traceback.print_exc()
                failure += 1
    if not DEBUGGING:
        if float(success + failure) == 0:
            print("NO REPLAYS WERE RUN.")
            print("Need files in: " + BASE_DIR)
        ratio = success / float(success + failure)
        print('success ratio:', ratio)
