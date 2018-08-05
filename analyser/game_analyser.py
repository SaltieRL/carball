import pandas as pd

from analyser.stats.stats import add_stats
from .hit import Hit


def analyse_game(game):
    print('Analysing Game: %s' % game)
    Hit.add_hits_to_game(game)

    # GOALS
    game.kickoff_frames = get_kickoff_frames(game)
    for goal_index, goal in enumerate(game.goals):
        goal_kickoff_frame = game.kickoff_frames[goal_index]
        goal_number = goal_index + 1
        goal.kickoff_frame = goal_kickoff_frame
        goal.goal_number = goal_number

    # FRAMES
    game.frames['goal_number'] = 0
    for goal in game.goals:
        game.frames.loc[goal.kickoff_frame: goal.frame_number, 'goal_number'] = goal.goal_number

    # HITS
    Hit.add_analytics_attributes(game)

    # STATS
    add_stats(game)


def get_kickoff_frames(game):
    ball_has_been_hit = game.frames.loc[:, 'ball_has_been_hit']
    last_frame_ball_has_been_hit = ball_has_been_hit.shift(1).rename('last_frame_ball_has_been_hit')
    ball_hit_dataframe = pd.concat([ball_has_been_hit, last_frame_ball_has_been_hit], axis=1)
    ball_hit_dataframe.fillna(False, inplace=True)
    # print(ball_hit_dataframe.head())

    kickoff_frames = ball_hit_dataframe[(ball_hit_dataframe['ball_has_been_hit']) &
                                        ~(ball_hit_dataframe['last_frame_ball_has_been_hit'])]

    # print(kickoff_frames.index.values)

    return kickoff_frames.index.values
