import logging
import pandas as pd

from json_parser.game import Game
from .metadata.ApiGame import ApiGame
from .saltie_hit import SaltieHit
from ..hit_detection.base_hit import BaseHit
from ..stats.stats import get_stats

logger = logging.getLogger(__name__)


class SaltieGame:

    def __init__(self, game: Game):
        logger.info("Creating SaltieGame from %s" % game)
        self.api_game = ApiGame.create_from_game(game)
        logger.info("Created .apiGame.")
        self.data_frame = self.create_data_df(game)
        logger.info("Created .data_frame")
        self.kickoff_frames = self.get_kickoff_frames(game)
        logger.info("Created .kickoff_frames")

        # FRAMES
        self.data_frame['goal_number'] = None
        for goal_number, goal in enumerate(game.goals):
            self.data_frame.loc[self.kickoff_frames[goal_number]: goal.frame_number, 'goal_number'] = goal_number

        # Set goal_number of frames that are post-last-goal to -1 (ie non None)
        if len(self.kickoff_frames) > len(self.api_game.goals):
            self.data_frame.loc[self.kickoff_frames[-1]:, 'goal_number'] = -1

        logger.info("Assigned goal_number in .data_frame")

        self.hits = BaseHit.get_hits_from_game(game)
        logger.info("Found %s hits." % len(self.hits))

        self.saltie_hits = SaltieHit.get_saltie_hits_from_game(self)
        logger.info("Analysed hits.")

        self.stats = get_stats(self)

    @staticmethod
    def get_kickoff_frames(game):
        if game.frames.loc[:, 'ball_has_been_hit'].any():
            ball_has_been_hit = game.frames.loc[:, 'ball_has_been_hit']
            last_frame_ball_has_been_hit = ball_has_been_hit.shift(1).rename('last_frame_ball_has_been_hit')
            ball_hit_dataframe = pd.concat([ball_has_been_hit, last_frame_ball_has_been_hit], axis=1)
            ball_hit_dataframe.fillna(False, inplace=True)

            kickoff_frames = ball_hit_dataframe[(ball_hit_dataframe['ball_has_been_hit']) &
                                                ~(ball_hit_dataframe['last_frame_ball_has_been_hit'])]
        else:
            logger.debug("No ball_has_been_hit?! Is this really old or what.")
            hit_team_no = game.ball.loc[:, 'hit_team_no']
            last_hit_team_no = hit_team_no.shift(1).rename('last_hit_team_no')
            hit_team_no_dataframe = pd.concat([hit_team_no, last_hit_team_no], axis=1)
            kickoff_frames = hit_team_no_dataframe[~(hit_team_no_dataframe['hit_team_no'].isnull()) &
                                                   (hit_team_no_dataframe['last_hit_team_no'].isnull())]

        return kickoff_frames.index.values

    @staticmethod
    def create_data_df(game: Game) -> pd.DataFrame:
        data_dict = {player.name: player.data for player in game.players}
        data_dict['ball'] = game.ball
        initial_df = pd.concat(data_dict, axis=1)

        dataframe = pd.concat([initial_df, game.frames], axis=1)
        return dataframe
