import pandas as pd

from carball.analysis.constants.field_constants import BALL_SIZE
from carball.generated.api import game_pb2


class CarryDetection:

    @staticmethod
    def filter_frames(data_frame: pd.DataFrame):
        valid_frames = data_frame[(data_frame.ball.pos_z > (BALL_SIZE + 1)) & (data_frame.ball.pos_z < 500)]
        return valid_frames

    @staticmethod
    def player_close_frames(valid_frames: pd.DataFrame, player_frames: pd.DataFrame):

        xy_distance = ((player_frames.pos_x - valid_frames.ball.pos_x) ** 2 +
                       (player_frames.pos_y - valid_frames.ball.pos_y) ** 2) ** 0.5
        close_players = valid_frames[(xy_distance < BALL_SIZE * 2) & (player_frames.pos_z < valid_frames.ball.pos_z)]
        return close_players
        # look up hits.
        # any hits by the same player within a continous set of valid frames should count as dribbles

    def put_together_dribbles(self, dribble_events, player_name: str, ):
        pass

    @staticmethod
    def generate_dribble_events(dribble_frames: pd.DataFrame, player_id, proto_game: game_pb2.Game):
        shifted = dribble_frames.index.to_series().shift(fill_value=0)
        neg_shifted = dribble_frames.index.to_series().shift(periods=-1, fill_value=0)
        start_frames = dribble_frames.index[abs(dribble_frames.index - shifted) > 3]
        end_frames = dribble_frames.index[abs(dribble_frames.index - neg_shifted) > 3]
        for i in range(len(start_frames)):
            total_time = dribble_frames.index.slice_locs(start_frames[i], end_frames[i])
            total_time = dribble_frames.iloc[total_time[0]:total_time[1]].game.delta.sum()
            if total_time < 1:
                # these are not valid dribbles we should skip
                continue
            ball_carry = proto_game.game_stats.ball_carries.add()
            ball_carry.start_frame_number = start_frames[i]
            ball_carry.end_frame_number = end_frames[i]
            ball_carry.player_id.id = player_id.id
