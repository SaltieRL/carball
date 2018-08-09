from typing import Dict, TYPE_CHECKING

import pandas as pd

from .possession.possession import PossessionStat

if TYPE_CHECKING:
    from ..saltie_game.saltie_game import SaltieGame


def get_stats(saltie_game: 'SaltieGame') -> Dict:
    # TODO: Get Tendencies working.
    return {
        # 'tendencies': TendenciesStat.get_tendencies(game),
        'possession': PossessionStat.get_possession(saltie_game)
    }


def get_goal_frame_data(game: 'SaltieGame', include_post_last_goal=True) -> pd.DataFrame:
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
