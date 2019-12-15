import logging

import pandas as pd

from ...json_parser.game import Game
logger = logging.getLogger(__name__)


class SaltieGame:

    @staticmethod
    def get_first_touch_frames(game):
        """
        Returns the frames for which the ball was touched in a valid way (if any touches happened)
        """
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
    def get_kickoff_frames(game):
        """
        Returns the frames between the kickoff countdown and the first touch occurring (if any touches happened).
        """
        if game.frames.loc[:, 'replicated_seconds_remaining'].any():
            ball_has_been_hit = game.frames.loc[:, 'replicated_seconds_remaining']
            last_frame_ball_has_been_hit = ball_has_been_hit.shift(1).rename('last_replicated_seconds_remaining')
            ball_hit_dataframe = pd.concat([ball_has_been_hit, last_frame_ball_has_been_hit], axis=1)
            ball_hit_dataframe.fillna(-1, inplace=True)

            countdown_start_frames = ball_hit_dataframe[(ball_hit_dataframe['replicated_seconds_remaining'] > 0) &
                                                  (ball_hit_dataframe['last_replicated_seconds_remaining'] == -1)]

            kickoff_frames = ball_hit_dataframe[(ball_hit_dataframe['replicated_seconds_remaining'] == 0) &
                                                (ball_hit_dataframe['last_replicated_seconds_remaining'] > 0)]

            countdown_indexes = countdown_start_frames.index.values

            if len(kickoff_frames.index.values) == len(countdown_indexes) == 1:
                reset_kickoff_index = kickoff_frames.index.values
            else:
                kickoff_count = 0
                reset_kickoff_index = []
                current_kickoff = None
                for kickoff in kickoff_frames.index.values:
                    if not kickoff_count + 1 < len(countdown_indexes):
                        break
                    if kickoff > countdown_indexes[kickoff_count] and kickoff < countdown_indexes[kickoff_count + 1]:
                        current_kickoff = kickoff
                    else:
                        reset_kickoff_index.append(current_kickoff)
                        kickoff_count += 1
                        current_kickoff = kickoff

                if current_kickoff is not None:
                    reset_kickoff_index.append(current_kickoff)

        else:
            logger.debug("No ball_has_been_hit?! Is this really old or what.")
            hit_team_no = game.ball.loc[:, 'hit_team_no']
            last_hit_team_no = hit_team_no.shift(1).rename('last_hit_team_no')
            hit_team_no_dataframe = pd.concat([hit_team_no, last_hit_team_no], axis=1)
            kickoff_frames = hit_team_no_dataframe[~(hit_team_no_dataframe['hit_team_no'].isnull()) &
                                                   (hit_team_no_dataframe['last_hit_team_no'].isnull())]

            reset_kickoff_index = kickoff_frames

        return reset_kickoff_index

    @staticmethod
    def create_data_df(game: Game) -> pd.DataFrame:
        data_dict = {player.name: player.data for player in game.players}
        data_dict['ball'] = game.ball
        initial_df = pd.concat(data_dict, axis=1)

        data_frame = pd.concat([initial_df, game.frames], axis=1)
        cols = []
        for c in data_frame.columns.values:
            if isinstance(c, str):
                cols.append(('game', c))
            else:
                cols.append(c)
        data_frame.columns = pd.MultiIndex.from_tuples(cols)
        return data_frame
