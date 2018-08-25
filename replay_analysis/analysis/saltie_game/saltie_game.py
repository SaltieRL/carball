import logging

import pandas

from ...json_parser.game import Game
logger = logging.getLogger(__name__)


class SaltieGame:

    @staticmethod
    def get_kickoff_frames(game):
        if game.frames.loc[:, 'ball_has_been_hit'].any():
            ball_has_been_hit = game.frames.loc[:, 'ball_has_been_hit']
            last_frame_ball_has_been_hit = ball_has_been_hit.shift(1).rename('last_frame_ball_has_been_hit')
            ball_hit_dataframe = pandas.concat([ball_has_been_hit, last_frame_ball_has_been_hit], axis=1)
            ball_hit_dataframe.fillna(False, inplace=True)

            kickoff_frames = ball_hit_dataframe[(ball_hit_dataframe['ball_has_been_hit']) &
                                                ~(ball_hit_dataframe['last_frame_ball_has_been_hit'])]
        else:
            logger.debug("No ball_has_been_hit?! Is this really old or what.")
            hit_team_no = game.ball.loc[:, 'hit_team_no']
            last_hit_team_no = hit_team_no.shift(1).rename('last_hit_team_no')
            hit_team_no_dataframe = pandas.concat([hit_team_no, last_hit_team_no], axis=1)
            kickoff_frames = hit_team_no_dataframe[~(hit_team_no_dataframe['hit_team_no'].isnull()) &
                                                   (hit_team_no_dataframe['last_hit_team_no'].isnull())]

        return kickoff_frames.index.values

    @staticmethod
    def create_data_df(game: Game) -> pandas.DataFrame:
        data_dict = {player.name: player.data for player in game.players}
        data_dict['ball'] = game.ball
        initial_df = pandas.concat(data_dict, axis=1)

        dataframe = pandas.concat([initial_df, game.frames], axis=1)
        cols = []
        for c in dataframe.columns.values:
            if isinstance(c, str):
                cols.append(('game', c))
            else:
                cols.append(c)
        dataframe.columns = pandas.MultiIndex.from_tuples(cols)
        return dataframe
