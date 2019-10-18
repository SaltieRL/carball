import json
import logging
import os
import platform as pt
import subprocess
from typing import List

from carball.rattletrap.rattletrap_utils import get_rattletrap_binaries, download_rattletrap, get_rattletrap_path, \
    get_binary_for_platform, get_all_binaries

logger = logging.getLogger(__name__)


class RattleTrapException(Exception):
    pass


def create_rattletrap_command(replay_path: str, output_path: str,
                              overwrite: bool = True, rattletrap_path: str = None) -> List[str]:
    """
    Takes a path to the replay and outputs the json of that replay.

    :param replay_path: Path to a specific replay.
    :param output_path: The output path of rattletrap.
    :param overwrite: True if we should recreate the json even if it already exists.
    :param rattletrap_path: Custom location for rattletrap executable.
    :return: The json created from rattle trap.
    """
    if rattletrap_path is None:
        rattletrap_path = get_rattletrap_path()
    binaries = get_all_binaries(rattletrap_path)

    if len(binaries) == 0 or not any('rattletrap' in file for file in binaries):
        logger.warning("Need to redownload rattletrap")
        download_rattletrap()
        binaries = get_rattletrap_binaries(rattletrap_path)
    binary = get_binary_for_platform(pt.system(), binaries)
    if binary is None:
        logger.warning('no binary!')
    cmd = [os.path.join(rattletrap_path, '{}'.format(binary)), '--compact', '-i',
           replay_path]
    if output_path:
        output_dirs = os.path.dirname(output_path)
        if not os.path.isdir(output_dirs) and output_dirs != '':
            os.makedirs(output_dirs)
        if overwrite or not os.path.isfile(output_path):
            cmd += ['--output', output_path]

    return cmd


def run_rattletrap_command(command: List[str], output_path: str):
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = proc.communicate()

    if proc.returncode != 0:
        # an error happened!
        err_msg = "%s. Code: %s" % (error.strip(), proc.returncode)
        raise RattleTrapException(err_msg)
    elif len(error):
        err_msg = "%s. Code: %s" % (error.strip(), proc.returncode)
        raise RattleTrapException(err_msg)

    if output:
        output = output.decode('utf8')
    if output_path:
        with open(output_path, encoding="utf8") as f:
            _json = json.load(f)
    else:
        _json = json.loads(output)
    return _json


def decompile_replay(replay_path: str, output_path: str, overwrite: bool = True, rattletrap_path: str = None):
    """
    Takes a path to the replay and outputs the json of that replay.

    :param replay_path: Path to a specific replay.
    :param output_path: The output path of rattletrap.
    :param overwrite: True if we should recreate the json even if it already exists.
    :param rattletrap_path: Custom location for rattletrap executable.
    :return: The json created from rattle trap.
    """
    command = create_rattletrap_command(replay_path, output_path, overwrite, rattletrap_path)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(" ".join(command))
    return run_rattletrap_command(command, output_path)
