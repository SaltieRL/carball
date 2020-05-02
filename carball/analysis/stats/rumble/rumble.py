import math
from typing import Dict, List

import pandas as pd

from carball.generated.api import game_pb2
from carball.generated.api.player_pb2 import Player
from carball.generated.api.stats.player_stats_pb2 import PlayerStats
from carball.generated.api.stats.team_stats_pb2 import TeamStats
from carball.generated.api.stats.events_pb2 import RumbleItemEvent
from carball.generated.api.stats.rumble_pb2 import PowerUp, RumbleStats
from carball.json_parser.game import Game
from carball.analysis.stats.stats import BaseStat
from carball.generated.api.metadata.game_metadata_pb2 import RANKED_RUMBLE, UNRANKED_RUMBLE


class RumbleItemStat(BaseStat):

    def calculate_player_stat(self, player_stat_map: Dict[str, PlayerStats], game: Game, proto_game: game_pb2.Game,
                              player_map: Dict[str, Player], data_frame: pd.DataFrame):
        if not is_rumble_enabled(game):
            return

        for player_key, stats in player_stat_map.items():
            player_name = player_map[player_key].name
            player_data_frame = data_frame[player_name]

            events = _get_power_up_events(player_map[player_key], player_data_frame, game,
                                          proto_game.game_stats.rumble_items)

            _calculate_rumble_stats(stats.rumble_stats, events, data_frame['game'])

    def calculate_team_stat(self, team_stat_list: Dict[int, TeamStats], game: Game, proto_game: game_pb2.Game,
                            player_map: Dict[str, Player], data_frame: pd.DataFrame):
        if not is_rumble_enabled(game):
            return

        orange_ids = list(map(lambda x: x.id.id, filter(lambda x: x.is_orange, player_map.values())))
        blue_ids = list(map(lambda x: x.id.id, filter(lambda x: not x.is_orange, player_map.values())))

        orange_events = list(filter(lambda x: x.player_id.id in orange_ids, proto_game.game_stats.rumble_items))
        blue_events = list(filter(lambda x: x.player_id.id in blue_ids, proto_game.game_stats.rumble_items))

        _calculate_rumble_stats(team_stat_list[1].rumble_stats, orange_events, data_frame['game'])
        _calculate_rumble_stats(team_stat_list[0].rumble_stats, blue_events, data_frame['game'])


def is_rumble_enabled(game: Game) -> bool:
    """
    Check whether rumble is enabled or not.

    :param game: parsed game object
    :return: True if rumble
    """
    if game is None or game.game_info is None:
        return False
    return game.game_info.playlist in [RANKED_RUMBLE, UNRANKED_RUMBLE] or \
           (game.game_info.rumble_mutator is not None and
            game.game_info.rumble_mutator.startswith('Archetypes.Mutators.SubRules.ItemsMode'))


def _get_power_up_events(player: Player, df: pd.DataFrame, game: Game, proto_rumble_item_events) \
        -> List[RumbleItemEvent]:
    """
    Finds the item get and item use events

    :param player: Player info protobuf. Get's the id from here
    :param df: player dataframe, assumes the frames between goal and kickoff are already discarded
    :param game: game object
    :param proto_rumble_item_events: protobuf repeated api.stats.RumbleItemEvent
    :return list of rumble events
    """
    events = []
    if 'power_up_active' in df and 'power_up' in df:
        if 'time_till_power_up' not in df:
            # someone actually uploaded a 10 second replay of the end of the match..
            df['time_till_power_up'] = math.nan
        df = df[['time_till_power_up', 'power_up', 'power_up_active']]

        ranges = [(game.kickoff_frames[i], game.kickoff_frames[i + 1]) for i in range(len(game.kickoff_frames) - 1)]
        ranges.append((game.kickoff_frames[-1], df.index[-1]))
        data_frames = map(lambda x: df.loc[x[0]:x[1] - 1], ranges)
        data_frames = map(_squash_power_up_df, data_frames)

        for data_frame in data_frames:

            if len(data_frame) == 0:
                # goal before items
                continue

            if not math.isnan(data_frame.iloc[0]['power_up_active']):
                # happens when kickoff starts with power ups after a goal that was scored less then 1 second before
                # time's up
                data_frame.loc[-1] = [0.0, math.nan, math.nan]
                data_frame.sort_index(inplace=True)

            prev_row = data_frame.iloc[0]
            proto_current_item = None
            demoed = False

            for i, row in data_frame.iloc[1:].iterrows():
                if math.isnan(prev_row['power_up_active']):
                    if row['power_up_active'] == False:
                        if not demoed:
                            # Rumble item get event
                            proto_current_item = proto_rumble_item_events.add()
                            proto_current_item.frame_number_get = i
                            proto_current_item.item = PowerUp.Value(row['power_up'].upper())
                            proto_current_item.player_id.id = player.id.id
                        else:
                            # back from the dead
                            demoed = False

                    if row['power_up_active'] == True:
                        # immediately used items (mostly bots)
                        tmp_item = proto_rumble_item_events.add()
                        tmp_item.frame_number_get = i
                        tmp_item.frame_number_use = i
                        tmp_item.item = PowerUp.Value(row['power_up'].upper())
                        tmp_item.player_id.id = player.id.id
                        events.append(tmp_item)

                elif prev_row['power_up_active'] == False:
                    if row['power_up_active'] == True or \
                            math.isnan(row['power_up_active']) and prev_row['power_up'] == 'ball_freeze':
                        # Rumble item use event
                        # When a spiked ball is frozen, there is not 'ball_freeze,True' row, it just gets deleted
                        # immediately
                        # Could also happen when the freeze is immediately broken
                        # in theory this should not happen with other power ups?
                        proto_current_item.frame_number_use = i
                        events.append(proto_current_item)
                        proto_current_item = None
                    elif math.isnan(row['power_up_active']):
                        # happens when player is demoed
                        demoed = True

                prev_row = row

            if proto_current_item is not None:
                # unused item
                events.append(proto_current_item)
                proto_current_item = None

    return events


def _squash_power_up_df(df: pd.DataFrame):
    """
    Remove all the rows with repeated 'power_up_active'. The frames are kept whenever the value is changed.
    """
    a = df['power_up_active']
    a = a.loc[(a.shift(-1).isnull() ^ a.isnull()) | (a.shift(1).isnull() ^ a.isnull()) | ~a.isnull()]
    a = a.loc[(a.shift(1) != a) | (a.shift(-1) != a)]

    # Drop any false values that come after true values
    while len(a.loc[(a.shift(1) == True) & (a == False)]) > 0:
        a = a.loc[(a.shift(1) != True) | (a != False)]

    df = pd.concat([df[['time_till_power_up', 'power_up']], a], axis=1, join='inner')

    return df


def _calculate_rumble_stats(rumble_proto: RumbleStats, events: List[RumbleItemEvent], game_df: pd.DataFrame):
    """
    Calculate rumble stats for all items

    :param rumble_proto: proto for stats
    :param events: list of rumble events
    :param game_df: game dataframe, used for getting the time delta
    """
    for power_up in set(PowerUp.values()):
        item_stats = _calculate_rumble_stats_for_power_up(events, power_up, game_df)

        rumble_item_proto = rumble_proto.rumble_items.add()
        rumble_item_proto.item = power_up
        rumble_item_proto.used = item_stats['used']
        rumble_item_proto.unused = item_stats['unused']
        rumble_item_proto.average_hold = item_stats['average_hold']


def _calculate_rumble_stats_for_power_up(events: List[RumbleItemEvent], power_up: int, game_df: pd.DataFrame) -> Dict:
    """
    Calculate rumble statistics (used, unused, average hold) based on rumble events.

    :param events: list of rumble events
    :param power_up: power up enum
    :param game_df: game dataframe, used for getting the time delta
    :return: stats
    """
    item_events = filter(lambda x: x.item == power_up, events)
    base = {'used': 0, 'unused': 0, 'average_hold': 0}

    for event in item_events:
        if event.frame_number_use != -1:
            base['used'] += 1
            base['average_hold'] += game_df.loc[event.frame_number_use]['time'] - \
                                    game_df.loc[event.frame_number_get]['time']
        else:
            base['unused'] += 1

    if base['used'] > 0:
        base['average_hold'] /= base['used']

    return base
