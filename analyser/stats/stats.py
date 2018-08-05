import pandas as pd

from .tendencies.tendencies import TendenciesStat
from .possession import PossessionStat
from game.game import Game


def add_stats(game: Game):
    # TODO: Get Tendencies working.
    game.stats = {
        # 'tendencies': TendenciesStat.get_tendencies(game),
        'posession': PossessionStat.get_possession(game)
    }


def get_goal_frame_data(game: Game, include_post_last_goal=True):
    """
    Adds .goal_data_frame attribute to game.
    Modified version of game.data_frame that does not include frames before kickoff/after goals
    :param game:
    :return:
    """
    goal_data_frames = [game.data_frame.loc[goal.kickoff_frame:goal.frame_number, :] for goal in game.goals]

    if include_post_last_goal:
        if len(game.kickoff_frames) > len(game.goals):
            goal_data_frames.append(game.data_frame.loc[game.kickoff_frames[-1]:, :])
    game.goal_data_frame = pd.concat(goal_data_frames)
