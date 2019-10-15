import logging
from typing import Dict

import pandas as pd

from carball.analysis.stats.stats import BaseStat
from carball.generated.api.player_pb2 import Player
from carball.generated.api import game_pb2
from carball.generated.api.stats.player_stats_pb2 import PlayerStats
from carball.generated.api.stats.team_stats_pb2 import TeamStats
from carball.json_parser.game import Game
from carball.analysis.stats.dropshot import is_dropshot

log = logging.getLogger(__name__)


class DropshotStats(BaseStat):

    def calculate_player_stat(self, player_stat_map: Dict[str, PlayerStats], game: Game, proto_game: game_pb2.Game,
                              player_map: Dict[str, Player], data_frame: pd.DataFrame):
        if not is_dropshot(game):
            return

        player_stats = {}

        for key, val in player_map.items():
            player_stats[key] = {
                'total': 0,
                'max': 0
            }

        for event in game.dropshot['damage_events']:
            ball_phase = data_frame['ball', 'dropshot_phase'].loc[event['frame_number'] - 1]
            max_dmg = 1
            if ball_phase == 1:
                max_dmg = 7
            elif ball_phase == 2:
                max_dmg = 19
            player_id = str(event['player'].online_id)
            player_stats[player_id]['total'] += len(event['tiles'])
            player_stats[player_id]['max'] += max_dmg

        self.apply_damage_stats(player_stat_map, player_stats)

    def calculate_team_stat(self, team_stat_list: Dict[int, TeamStats], game: Game, proto_game: game_pb2.Game,
                            player_map: Dict[str, Player], data_frame: pd.DataFrame):
        if not is_dropshot(game):
            return

        team_stats = {
            0: {'total': 0, 'max': 0},
            1: {'total': 0, 'max': 0}
        }

        for event in game.dropshot['damage_events']:
            ball_phase = data_frame['ball', 'dropshot_phase'].loc[event['frame_number'] - 1]
            max_dmg = 1
            if ball_phase == 1:
                max_dmg = 7
            elif ball_phase == 2:
                max_dmg = 19

            team = event['player'].is_orange
            team_stats[team]['total'] += len(event['tiles'])
            team_stats[team]['max'] += max_dmg

        self.apply_damage_stats(team_stat_list, team_stats)

    def calculate_stat(self, proto_stat, game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player],
                       data_frame: pd.DataFrame):
        if not is_dropshot(game):
            return

        tile_stats = {}
        damaged = 0
        destroyed = 0

        for event in game.dropshot['damage_events']:
            for tile_damage in event['tiles']:
                tile_id = tile_damage[0]
                if tile_id not in tile_stats:
                    tile_stats[tile_id] = 1
                else:
                    tile_stats[tile_id] += 1

                if tile_damage[1] == 1:
                    damaged += 1
                elif tile_damage[1] == 2:
                    destroyed += 1

        for tile_id, total_damage in tile_stats.items():
            damage_stat_proto = proto_game.game_stats.dropshot_stats.tile_stats.damage_stats.add()
            damage_stat_proto.id = tile_id
            damage_stat_proto.total_damage = total_damage

        proto_game.game_stats.dropshot_stats.tile_stats.damaged_tiles = damaged
        proto_game.game_stats.dropshot_stats.tile_stats.destroyed_tiles = destroyed

    def apply_damage_stats(self, stat_list, game_stats):
        for key, stats in stat_list.items():
            stats.dropshot_stats.total_damage = game_stats[key]['total']

            if game_stats[key]['max'] > 0:
                stats.dropshot_stats.damage_efficiency = game_stats[key]['total'] / game_stats[key]['max']
            else:
                stats.dropshot_stats.damage_efficiency = 0
