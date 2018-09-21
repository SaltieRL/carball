import json
import os
import subprocess
import logging
import sys
import platform as pt

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from carball.analysis.analysis_manager import AnalysisManager
from carball.extras.per_goal_analysis import PerGoalAnalysis
from carball.json_parser.sanity_check.sanity_check import SanityChecker
from carball.json_parser.game import Game
from carball.controls.controls import ControlsCreator


logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(__file__)


def decompile_replay(replay_path, output_path, overwrite=True):
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
    output_dirs = os.path.dirname(output_path)
    if not os.path.isdir(output_dirs) and output_dirs != '':
        os.makedirs(output_dirs)
    if overwrite or not os.path.isfile(output_path):
        cmd = [os.path.join(os.path.join(BASE_DIR, 'rattletrap'), '{}'.format(binary)), '--compact', '-i',
               replay_path,
               '--output',
               output_path]
        logger.debug(" ".join(cmd))
        subprocess.check_output(cmd)
    _json = json.load(open(output_path, encoding="utf8"))
    return _json


def analyze_replay_file(replay_path: str, output_path: str, overwrite=True, controls: ControlsCreator=None,
                        sanity_check: SanityChecker=None, analysis_per_goal=False):
    """
    Decompile and analyze a replay file.

    :param replay_path: Path to replay file
    :param output_path: Path to write JSON
    :param overwrite: If to overwrite JSON (suggest True if speed is not an issue)
    :param controls: Generate controls from the replay using our best guesses (ALPHA)
    :param sanity_check: Run sanity check to make sure we analyzed correctly (BETA)
    :param analysis_per_goal: Runs the analysis per a goal instead of the replay as a whole
    :return: AnalysisManager of game with analysis.
    """
    _json = decompile_replay(replay_path, output_path, overwrite=overwrite)
    game = Game()
    game.initialize(loaded_json=_json)
    # get_controls(game)  # TODO: enable and optimise.
    if sanity_check is not None:
        sanity_check.check_game(game)
    if analysis_per_goal:
        analysis = PerGoalAnalysis(game)
    else:
        analysis = AnalysisManager(game)
    analysis.create_analysis()

    if controls is not None:
        controls.get_controls(game)

    return analysis


if __name__ == '__main__':
    from carball.tests.analysis_test import __test_replays
    __test_replays(BASE_DIR)
