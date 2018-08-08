import pandas as pd

from json_parser.game import Game
from .metadata.ApiGame import ApiGame
from .saltie_hit import SaltieHit
from ..hit_detection.base_hit import BaseHit
from ..stats.stats import get_stats


class SaltieGame:

    def __init__(self, game: Game):
        self.api_game = ApiGame.create_from_game(game)

        self.data_frame = game.data_frame

        self.kickoff_frames = self.get_kickoff_frames(game)

        # FRAMES
        self.data_frame['goal_number'] = 0
        for goal_number, goal in enumerate(game.goals):
            self.data_frame.loc[self.kickoff_frames[goal_number]: goal.frame_number, 'goal_number'] = goal_number

        self.hits = BaseHit.get_hits_from_game(game)
        self.saltie_hits = SaltieHit.get_saltie_hits_from_game(self)

        self.stats = get_stats(game)

    @staticmethod
    def get_kickoff_frames(game):
        ball_has_been_hit = game.frames.loc[:, 'ball_has_been_hit']
        last_frame_ball_has_been_hit = ball_has_been_hit.shift(1).rename('last_frame_ball_has_been_hit')
        ball_hit_dataframe = pd.concat([ball_has_been_hit, last_frame_ball_has_been_hit], axis=1)
        ball_hit_dataframe.fillna(False, inplace=True)

        kickoff_frames = ball_hit_dataframe[(ball_hit_dataframe['ball_has_been_hit']) &
                                            ~(ball_hit_dataframe['last_frame_ball_has_been_hit'])]

        return kickoff_frames.index.values
