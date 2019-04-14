import math
from typing import Dict

import pandas as pd

from carball.generated.api import game_pb2
from carball.generated.api.player_pb2 import Player
from carball.generated.api.stats.player_stats_pb2 import PlayerStats
from carball.generated.api.stats.team_stats_pb2 import TeamStats
from carball.json_parser.game import Game
from carball.analysis.stats.stats import BaseStat
from carball.generated.api.metadata.game_metadata_pb2 import RANKED_RUMBLE, UNRANKED_RUMBLE

_BASE = {
    'ball_freeze': 0,
    'ball_grappling_hook': 0,
    'ball_lasso': 0,
    'ball_spring': 0,
    'ball_velcro': 0,
    'batarang': 0,
    'boost_override': 0,
    'car_spring': 0,
    'gravity_well': 0,
    'strong_hit': 0,
    'swapper': 0,
    'tornado': 0
}


class RumbleItemStat(BaseStat):

    def calculate_player_stat(self, player_stat_map: Dict[str, PlayerStats], game: Game, proto_game: game_pb2.Game,
                              player_map: Dict[str, Player], data_frame: pd.DataFrame):
        if game.game_info.playlist not in [RANKED_RUMBLE, UNRANKED_RUMBLE]:
            return

        for player_key, stats in player_stat_map.items():
            player_name = player_map[player_key].name
            player_data_frame = data_frame[player_name]

            _get_power_up_events(player_map[player_key], player_data_frame, game, proto_game.game_stats.rumble_items)

            rumble_proto = stats.rumble_item_usage

            pass

            # rumble_proto.ball_freeze = item_stats['ball_freeze']
            # rumble_proto.ball_grappling_hook = item_stats['ball_grappling_hook']
            # rumble_proto.ball_lasso = item_stats['ball_lasso']
            # rumble_proto.ball_spring = item_stats['ball_spring']
            # rumble_proto.ball_velcro = item_stats['ball_velcro']
            # rumble_proto.boost_override = item_stats['boost_override']
            # rumble_proto.car_spring = item_stats['car_spring']
            # rumble_proto.gravity_well = item_stats['gravity_well']
            # rumble_proto.strong_hit = item_stats['strong_hit']
            # rumble_proto.swapper = item_stats['swapper']
            # rumble_proto.tornado = item_stats['tornado']

    def calculate_team_stat(self, team_stat_list: Dict[int, TeamStats], game: Game, proto_game: game_pb2.Game,
                            player_map: Dict[str, Player], data_frame: pd.DataFrame):
        if game.game_info.playlist not in [RANKED_RUMBLE, UNRANKED_RUMBLE]:
            return

        for key, team in team_stat_list.items():
            rumble_proto = team.rumble_item_usage

            rumble_proto.ball_freeze = 0
            rumble_proto.ball_grappling_hook = 0
            rumble_proto.ball_lasso = 0
            rumble_proto.ball_spring = 0
            rumble_proto.ball_velcro = 0
            rumble_proto.boost_override = 0
            rumble_proto.car_spring = 0
            rumble_proto.gravity_well = 0
            rumble_proto.strong_hit = 0
            rumble_proto.swapper = 0
            rumble_proto.tornado = 0

        for key, player in player_map.items():
            rumble_proto = team_stat_list[player.is_orange].rumble_item_usage
            player_rumble_stats = player.stats.rumble_item_usage

            rumble_proto.ball_freeze += player_rumble_stats.ball_freeze
            rumble_proto.ball_grappling_hook += player_rumble_stats.ball_grappling_hook
            rumble_proto.ball_lasso += player_rumble_stats.ball_lasso
            rumble_proto.ball_spring += player_rumble_stats.ball_spring
            rumble_proto.ball_velcro += player_rumble_stats.ball_velcro
            rumble_proto.boost_override += player_rumble_stats.boost_override
            rumble_proto.car_spring += player_rumble_stats.car_spring
            rumble_proto.gravity_well += player_rumble_stats.gravity_well
            rumble_proto.strong_hit += player_rumble_stats.strong_hit
            rumble_proto.swapper += player_rumble_stats.swapper
            rumble_proto.tornado += player_rumble_stats.tornado


def _get_power_up_events(player: Player, df: pd.DataFrame, game: Game, proto_rumble_item_events):
    """
    Finds the item get and item use events

    :param player: Player info protobuf. Get's the id from here
    :param df: player dataframe, assumes the frames between goal and kickoff are already discarded
    :param game: game object
    :param proto_rumble_item_events: protobuf repeated api.stats.RumbleItemEvent
    """
    if 'power_up_active' in df and 'power_up' in df:
        df = df[['time_till_power_up', 'power_up', 'power_up_active']]

        ranges = [(game.kickoff_frames[i], game.kickoff_frames[i + 1]) for i in range(len(game.kickoff_frames) - 1)]
        data_frames = map(lambda x: df.loc[x[0]:x[1] - 1], ranges)
        data_frames = list(map(_squash_power_up_df, data_frames))

        for data_frame in data_frames:

            prev_row = data_frame.iloc[0]
            proto_current_item = None

            for i, row in data_frame.iloc[1:].iterrows():
                if math.isnan(prev_row['power_up_active']):
                    if row['power_up_active'] == False:
                        # Rumble item get event
                        proto_current_item = proto_rumble_item_events.add()
                        proto_current_item.frame_number_get = i
                        proto_current_item.item = row['power_up']
                        proto_current_item.player_id.id = player.id.id

                elif prev_row['power_up_active'] == False:
                    if row['power_up_active'] == True:
                        # Rumble item use event
                        proto_current_item.frame_number_use = i
                        proto_current_item = None
                    elif math.isnan(row['power_up_active']) and prev_row['power_up'] == 'ball_freeze':
                        # When a spiked ball is frozen, there is not 'ball_freeze,True' row, it just gets deleted
                        # immediately
                        # Could also happen when the freeze is immediately broken
                        # in theory this should not happen with other power ups?
                        proto_current_item.frame_number_use = i
                        proto_current_item = None

                prev_row = row


def _squash_power_up_df(df: pd.DataFrame):
    """
    Remove all the rows with repeated 'power_up_active'. The frames are kept whenever the value is changed.
    """
    a = df['power_up_active']
    a = a.loc[(a.shift(-1).isnull() ^ a.isnull()) | (a.shift(1).isnull() ^ a.isnull()) | ~a.isnull()]
    a = a.loc[(a.shift(1) != a) | (a.shift(-1) != a)]

    df = pd.concat([df[['time_till_power_up', 'power_up']], a], axis=1, join='inner')

    return df
