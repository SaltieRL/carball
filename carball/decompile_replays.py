import logging
import os
from boxcars_py import parse_replay

from carball.analysis.analysis_manager import AnalysisManager
from carball.controls.controls import ControlsCreator
from carball.extras.per_goal_analysis import PerGoalAnalysis
from carball.json_parser.game import Game
from carball.json_parser.sanity_check.sanity_check import SanityChecker

BASE_DIR = os.path.dirname(__file__)


def decompile_replay(replay_path):
    """
    Takes a path to the replay and outputs the json of that replay.

    :param replay_path: Path to a specific replay.
    :return: The object created from boxcars.
    """
    with open(replay_path, 'rb') as f:
        buf = f.read()
    return parse_replay(buf)


def analyze_replay_file(replay_path: str, controls: ControlsCreator = None,
                        sanity_check: SanityChecker = None, analysis_per_goal=False,
                        logging_level=logging.NOTSET,
                        calculate_intensive_events: bool = False,
                        clean: bool = True):
    """
    Decompile and analyze a replay file.

    :param replay_path: Path to replay file
    :param controls: Generate controls from the replay using our best guesses (ALPHA)
    :param sanity_check: Run sanity check to make sure we analyzed correctly (BETA)
    :param analysis_per_goal: Runs the analysis per a goal instead of the replay as a whole
    :param force_full_analysis: If True full analysis will be performed even if checks say it should not.
    :param logging_level: Sets the logging level globally across carball
    :param calculate_intensive_events: Indicates if expensive calculations should run to include additional stats.
    :param clean: Indicates if useless/invalid data should be found and removed.
    :return: AnalysisManager of game with analysis.
    """

    if logging_level != logging.NOTSET:
        logging.getLogger('carball').setLevel(logging_level)

    _json = decompile_replay(replay_path)
    game = Game()
    game.initialize(loaded_json=_json)
    # get_controls(game)  # TODO: enable and optimise.
    if sanity_check is not None:
        sanity_check.check_game(game)
    if analysis_per_goal:
        analysis = PerGoalAnalysis(game)
    else:
        analysis = AnalysisManager(game)
    analysis.create_analysis(calculate_intensive_events=calculate_intensive_events, clean=clean)

    if controls is not None:
        controls.get_controls(game)

    return analysis


if __name__ == '__main__':
    from carball.tests.analysis_test import __test_replays

    __test_replays(BASE_DIR)
