from typing import Dict

import pandas as pd

from ..saltie_game.saltie_game import SaltieGame
from .possession.possession import PossessionStat
from json_parser.game import Game


def get_stats(game: Game) -> Dict:
    # TODO: Get Tendencies working.
    return {
        # 'tendencies': TendenciesStat.get_tendencies(game),
        'posession': PossessionStat.get_possession(game)
    }


def get_goal_frame_data(game: SaltieGame, include_post_last_goal=True) -> pd.DataFrame:
    """
    Adds .goal_data_frame attribute to game.
    Modified version of game.data_frame that does not include frames before kickoff/after goals
    :param game:
    :return:
    """
    goal_data_frames = [game.data_frame.loc[goal.kickoff_frame:goal.frame_number, :] for goal in game.api_game.goals]

    if include_post_last_goal:
        if len(game.kickoff_frames) > len(game.api_game.goals):
            goal_data_frames.append(game.data_frame.loc[game.kickoff_frames[-1]:, :])

    return pd.concat(goal_data_frames)
