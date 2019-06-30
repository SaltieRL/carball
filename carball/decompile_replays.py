import logging
import os

from carball.analysis.analysis_manager import AnalysisManager
from carball.controls.controls import ControlsCreator
from carball.extras.per_goal_analysis import PerGoalAnalysis
from carball.json_parser.game import Game
from carball.json_parser.sanity_check.sanity_check import SanityChecker
from carball.rattletrap import run_rattletrap

logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(__file__)


def decompile_replay(replay_path, output_path: str = None, overwrite: bool = True, rattletrap_path: str = None):
    """
    Takes a path to the replay and outputs the json of that replay.

    :param replay_path: Path to a specific replay.
    :param output_path: The output path of rattletrap.
    :param overwrite: True if we should recreate the json even if it already exists.
    :param rattletrap_path: Custom location for rattletrap executable. Path to folder.
    :return: The json created from rattle trap.
    """
    return run_rattletrap.decompile_replay(replay_path, output_path, overwrite, rattletrap_path)


def analyze_replay_file(replay_path: str, output_path: str = None, overwrite=True, controls: ControlsCreator = None,
                        sanity_check: SanityChecker = None, analysis_per_goal=False, rattletrap_path: str = None):
    """
    Decompile and analyze a replay file.

    :param replay_path: Path to replay file
    :param output_path: Path to write JSON
    :param overwrite: If to overwrite JSON (suggest True if speed is not an issue)
    :param controls: Generate controls from the replay using our best guesses (ALPHA)
    :param sanity_check: Run sanity check to make sure we analyzed correctly (BETA)
    :param analysis_per_goal: Runs the analysis per a goal instead of the replay as a whole
    :param rattletrap_path: Custom location for rattletrap executable. Path to folder.
    :param force_full_analysis: If True full analysis will be performed even if checks say it should not.
    :return: AnalysisManager of game with analysis.
    """
    _json = decompile_replay(replay_path, output_path=output_path, overwrite=overwrite, rattletrap_path=rattletrap_path)
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
