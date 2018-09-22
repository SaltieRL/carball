import glob
import gzip
import os
import shutil
import subprocess
import traceback

from google.protobuf.json_format import MessageToJson

from carball.controls.controls import ControlsCreator
from carball.decompile_replays import analyze_replay_file
from carball.json_parser.sanity_check.sanity_check import SanityChecker


def create_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def __test_replays(BASE_DIR):
    import logging

    ROOT_DIR = os.path.dirname(BASE_DIR)
    OUTPUT_DIR = os.path.join(ROOT_DIR, 'output')

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    MOVE_WORKING = True
    DEBUGGING = True
    success = 0
    failure = 0
    create_dir(OUTPUT_DIR)

    for filepath in glob.iglob(ROOT_DIR + '/**/*.replay', recursive=True):
        logger.info('decompiling %s', filepath)
        if "output" in filepath:
            continue
        base_file = os.path.basename(filepath)
        json_path = os.path.join(OUTPUT_DIR, 'replays/decompiled/{}'.format(base_file.replace(".replay", ".json")))
        proto_path = os.path.join(OUTPUT_DIR, 'replays/protos/{}'.format(base_file.replace(".replay", ".pts")))
        pandas_path = os.path.join(OUTPUT_DIR, 'replays/pandas/{}'.format(base_file.replace(".replay", ".gzip")))

        create_dir(os.path.dirname(json_path))
        create_dir(os.path.dirname(proto_path))
        create_dir(os.path.dirname(pandas_path))

        if DEBUGGING:
            try:
                analysis_manager = analyze_replay_file(filepath, json_path,
                                                       controls=ControlsCreator(), analysis_per_goal=False,
                                                       sanity_check=SanityChecker())
                with open(os.path.join(OUTPUT_DIR, 'game.json'), 'w') as f:
                    f.write(MessageToJson(analysis_manager.protobuf_game))
            except subprocess.CalledProcessError as e:
                traceback.print_exc()
        else:
            try:
                analysis_manager = analyze_replay_file(filepath, json_path)
                with open(proto_path, 'wb') as fo:
                    analysis_manager.write_proto_out_to_file(fo)
                with gzip.open(pandas_path, 'wb') as fo:
                    analysis_manager.write_pandas_out_to_file(fo)
                if MOVE_WORKING:
                    shutil.move(filepath, os.path.join('replays', 'working', filepath))
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
