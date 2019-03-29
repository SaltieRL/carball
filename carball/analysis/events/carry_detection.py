import pandas as pd

from carball.analysis.constants.field_constants import BALL_SIZE
from carball.generated.api import game_pb2
from carball.generated.api.player_pb2 import Player


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
        return close_players, xy_distance, player_frames
        # look up hits.
        # any hits by the same player within a continous set of valid frames should count as dribbles

    def put_together_dribbles(self, dribble_events, player_name: str):
        pass

    @staticmethod
    def get_distance(player_frames, start, end):
        x1 = player_frames.pos_x[start]
        y1 = player_frames.pos_y[start]

        x2 = player_frames.pos_x[end]
        y2 = player_frames.pos_y[end]

        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

    @staticmethod
    def create_dribble_events(valid_frames: pd.DataFrame, player: Player, proto_game: game_pb2.Game):
        """
        Gets all of the dribble events and adds them to the protobuf for each individual palyer.
        """
        dribble_frames, xy_distance, player_frames = CarryDetection.player_close_frames(valid_frames,
                                                                                        valid_frames[player.name])

        shifted = dribble_frames.index.to_series().shift(fill_value=0)
        neg_shifted = dribble_frames.index.to_series().shift(periods=-1, fill_value=0)
        start_frames = dribble_frames.index[abs(dribble_frames.index - shifted) > 3]
        end_frames = dribble_frames.index[abs(dribble_frames.index - neg_shifted) > 3]
        for i in range(len(start_frames)):
            total_time = dribble_frames.index.slice_locs(start_frames[i], end_frames[i])
            carry_frames = dribble_frames.iloc[total_time[0]:total_time[1]]
            total_time = carry_frames.game.delta.sum()
            if total_time < 1:
                # these are not valid dribbles we should skip
                continue

            player_frames = carry_frames[player.name]

            ball_carry = proto_game.game_stats.ball_carries.add()
            ball_carry.start_frame_number = start_frames[i]
            ball_carry.end_frame_number = end_frames[i]
            ball_carry.player_id.id = player.id.id
            ball_carry.carry_time = total_time
            ball_carry.distance_traveled = CarryDetection.get_distance(player_frames, start_frames[i], end_frames[i])

            z_distance = carry_frames.ball.pos_z - player_frames.pos_z
            xy_carry = xy_distance[start_frames[i]:end_frames[i]]

            # adding stats for this carry
            carry_stats = ball_carry.carry_stats
            carry_stats.average_xy_distance = xy_carry.mean()
            carry_stats.average_z_distance = z_distance.mean()
            carry_stats.average_ball_z_velocity = carry_frames.ball.vel_z.mean()
            carry_stats.variance_xy_distance = xy_carry.var()
            carry_stats.variance_z_distance = z_distance.var()
            carry_stats.variance_ball_z_velocity = carry_frames.ball.vel_z.var()
            carry_stats.average_carry_speed = ((player_frames.vel_x ** 2 + player_frames.vel_y ** 2) ** 0.5).mean()
