import logging
import os
import subprocess
import json
import platform as pt
from typing import List

logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def create_rattletrap_command(replay_path: str, output_path: str, overwrite: bool=True) -> List[str]:
    """
    Takes a path to the replay and outputs the json of that replay.

    :param replay_path: Path to a specific replay.
    :param output_path: The output path of rattletrap.
    :param overwrite: True if we should recreate the json even if it already exists.
    :return: The json created from rattle trap.
    """
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
    cmd = [os.path.join(os.path.join(BASE_DIR, 'rattletrap'), '{}'.format(binary)), '--compact', '-i',
           replay_path]
    if output_path:
        output_dirs = os.path.dirname(output_path)
        if not os.path.isdir(output_dirs) and output_dirs != '':
            os.makedirs(output_dirs)
        if overwrite or not os.path.isfile(output_path):
            cmd += ['--output', output_path]

    return cmd


def run_rattletrap_command(command: List[str], output_path: str):
    proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    output = proc.stdout.read()
    if output:
        output = output.decode('utf8')
    if output_path:
        with open(output_path, encoding="utf8") as f:
            _json = json.load(f)
    else:
        _json = json.loads(output)
    return _json


def decompile_replay(replay_path: str, output_path: str, overwrite: bool=True):
    """
    Takes a path to the replay and outputs the json of that replay.

    :param replay_path: Path to a specific replay.
    :param output_path: The output path of rattletrap.
    :param overwrite: True if we should recreate the json even if it already exists.
    :return: The json created from rattle trap.
    """
    command = create_rattletrap_command(replay_path, output_path, overwrite)
    logger.debug(" ".join(command))
    return run_rattletrap_command(command, output_path)
