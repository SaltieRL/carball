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

            item_stats = _get_power_up_stats(player_data_frame, game)

            rumble_proto = stats.rumble_item_usage

            rumble_proto.ball_freeze = item_stats['ball_freeze']
            rumble_proto.ball_grappling_hook = item_stats['ball_grappling_hook']
            rumble_proto.ball_lasso = item_stats['ball_lasso']
            rumble_proto.ball_spring = item_stats['ball_spring']
            rumble_proto.ball_velcro = item_stats['ball_velcro']
            rumble_proto.boost_override = item_stats['boost_override']
            rumble_proto.car_spring = item_stats['car_spring']
            rumble_proto.gravity_well = item_stats['gravity_well']
            rumble_proto.strong_hit = item_stats['strong_hit']
            rumble_proto.swapper = item_stats['swapper']
            rumble_proto.tornado = item_stats['tornado']

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


def _get_power_up_stats(df: pd.DataFrame, game: Game):
    all_items = dict(_BASE)

    if 'power_up_active' in df and 'power_up' in df:
        df = df[['power_up', 'power_up_active']]
        df = _squash_power_up_df(df, game)

        used_items = df.groupby('power_up')['power_up'].size().to_dict()

        all_items.update(used_items)

    all_items['ball_lasso'] += all_items.pop('batarang')

    return all_items


def _squash_power_up_df(df: pd.DataFrame, game: Game):
    a = df['power_up_active']
    a = a.loc[(a.shift(1).isnull() ^ a.isnull()) | ~a.isnull()]
    a = a.loc[(a.shift(1) != a) | (a.shift(-1) != a)]

    df = pd.concat([df['power_up'], a], axis=1, join='inner')

    mask = []
    prev_false = False
    prev_power_up = None

    for i, row in df.iterrows():
        if math.isnan(row['power_up_active']):
            if prev_false and prev_power_up == 'ball_freeze':
                # When a spiked ball is frozen, there is not 'ball_freeze,True' row, it just gets deleted immediately
                # Could also happen when the freeze is immediately broken
                # in theory this should not happen with other power ups
                ball_reset = i in game.kickoff_frames
                if not ball_reset:
                    mask[-1] = True

            mask.append(False)
            prev_false = False
        elif not row['power_up_active']:
            mask.append(False)
            prev_false = True
            prev_power_up = row['power_up']
        else:
            mask.append(prev_false)
            prev_false = False
            prev_power_up = row['power_up']

    return df[mask]
