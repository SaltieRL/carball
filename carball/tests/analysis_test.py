import glob
import gzip
import os
import shutil
import subprocess
import traceback
from io import BytesIO

from google.protobuf.json_format import MessageToJson

from carball.analysis.utils.pandas_manager import PandasManager
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

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    MOVE_WORKING = True
    DEBUGGING = True
    success = 0
    failure = 0
    create_dir(OUTPUT_DIR)
    sanity_check = SanityChecker()
    sanity_check = None

    for filepath in glob.iglob(ROOT_DIR + '/**carball/replays/*.replay', recursive=True):
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
                                                       sanity_check=sanity_check)
                id = analysis_manager.protobuf_game.game_metadata.id
                with open(os.path.join(OUTPUT_DIR, id + 'game.json'), 'w') as f:
                    f.write(MessageToJson(analysis_manager.protobuf_game))
                    bytes = PandasManager.write_pandas_to_buffer_for_tooling(analysis_manager.get_data_frame(),
                                                           analysis_manager.get_protobuf_data().players)
                    with open(pandas_path, 'wb') as fo:
                        fo.write(bytes)

                data_frame = PandasManager.safe_read_pandas_to_memory(BytesIO(analysis_manager.df_bytes))
                logger.info('length of decoded pandas %i', len(data_frame))
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

if __name__ == "__main__":
    __test_replays(os.path.dirname(os.getcwd()))
