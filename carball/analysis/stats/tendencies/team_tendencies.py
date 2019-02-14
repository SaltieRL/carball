from typing import Dict, List

import pandas as pd

from carball.analysis.constants.basic_math import position_column_names
from carball.analysis.constants.playlist import get_team_size_from_game
from carball.analysis.stats.possession.ball_distances import BallDistanceStat
from carball.generated.api.team_pb2 import Team

from ....analysis.stats.tendencies.positional_tendencies import PositionalTendencies
from ....generated.api import game_pb2
from ....generated.api.player_pb2 import Player
from ....generated.api.stats.team_stats_pb2 import TeamStats
from ....json_parser.game import Game

# MAX_CLUMP_DISTANCE = math.sqrt(8192**2 + 10240**2) / 8
MAX_CLUMP_DISTANCE = 3278
MIN_BOONDOCKS_DISTANCE = 7000


class TeamTendencies(PositionalTendencies):

    def calculate_team_stat(self, team_stat_list: Dict[int, TeamStats], game: Game, proto_game: game_pb2.Game,
                            player_map: Dict[str, Player], data_frame: pd.DataFrame):
        for team in proto_game.teams:
            team_size = get_team_size_from_game(proto_game)
            if len(team.player_ids) <= 1 or team_size <= 1:
                # center of mass does not matter for 1s games
                continue
            player_names = [player_map[player_id.id].name for player_id in team.player_ids]
            center_of_mass = self.calculate_team_center(data_frame, player_names)
            self.get_team_tendencies(team, data_frame, center_of_mass)

            self.calculate_displacements(team, player_map, center_of_mass, data_frame, team_size)

    def calculate_team_center(self, data_frame, list_of_players) -> (pd.DataFrame, List[pd.DataFrame]):
        players = []
        for player in list_of_players:
            player_frame = data_frame[player][position_column_names]
            players.append(player_frame)

        combined = pd.concat(players)
        center_position = combined.groupby(combined.index).mean()
        return center_position

    def get_team_tendencies(self, team: Team, data_frame: pd.DataFrame, team_center: pd.DataFrame):
        self.get_tendencies(data_frame, team_center, data_frame['ball'],
                            team.is_orange, team.stats.center_of_mass.positional_tendencies,
                            self.map_player_attributes_to_predicates)

    def calculate_displacements(self, team: Team, player_map: Dict[str, Player],
                                center_of_mass: pd.DataFrame, data_frame: pd.DataFrame, team_size: int):
        player_distances_data_frame, player_distance_times, _ \
            = BallDistanceStat.calculate_player_distance_to_location(player_map, data_frame, center_of_mass)

        average_distances = []
        for player_id in team.player_ids:
            player = player_map[player_id.id]
            average_distance_from_center = player_distances_data_frame[player.id.id].mean(skipna=True)
            self.set_player_stats(player, player_distance_times, average_distance_from_center, team_size)
            player_position_with_time = pd.concat([data_frame[player.name][position_column_names],
                                 data_frame['game', 'delta'].rename('delta')], axis=1)
            if team_size > 2:
                self.set_player_positional_stats(player, center_of_mass, player_position_with_time)

            average_distances.append(average_distance_from_center)

        team.stats.center_of_mass.average_distance_from_center = sum(average_distances) / len(average_distances)

        max_distances = player_distances_data_frame.max(axis=1)
        team.stats.center_of_mass.average_max_distance_from_center = max_distances.mean(skipna=True)

        max_distances_with_delta = pd.concat([player_distances_data_frame,
                                              data_frame['game', 'delta'].rename('delta')], axis=1)

        if len(team.player_ids) == 2:
            clump_distance = MAX_CLUMP_DISTANCE / 2
        else:
            clump_distance = MAX_CLUMP_DISTANCE

        close_frames = max_distances < clump_distance
        time_clumped = max_distances_with_delta[close_frames]['delta'].sum()
        team.stats.center_of_mass.time_clumped = time_clumped

        if len(team.player_ids) == 2:
            boondocks_distance = MIN_BOONDOCKS_DISTANCE / 2
        else:
            boondocks_distance = MIN_BOONDOCKS_DISTANCE

        boondocks_frames = max_distances > boondocks_distance
        time_boondocks = max_distances_with_delta[boondocks_frames]['delta'].sum()
        team.stats.center_of_mass.time_boondocks = time_boondocks

    def set_player_stats(self, player, player_distance_times, average_distance_from_center, team_size):
        player.stats.averages.average_distance_from_center = average_distance_from_center
        player_id = player.id.id
        distance = player.stats.distance

        if team_size > 2:
            try:
                distance.time_closest_to_team_center = player_distance_times['closest_player'][player_id]
                distance.time_furthest_from_team_center = player_distance_times['furthest_player'][player_id]
            except (AttributeError, KeyError) as e:
                distance.time_closest_to_team_center = 0
                distance.time_furthest_from_team_center = 0

    def get_flipped_dataframes(self, data_frames: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        new_dataframes = {
            _k: _v.copy() for _k, _v in data_frames.items()
        }

        for data_frame in new_dataframes.values():
            data_frame.pos_y *= -1

        return new_dataframes

    def set_player_positional_stats(self, player, center_of_mass, distances_with_time):
        y_position = pd.concat([distances_with_time['pos_y'].rename('car_y'),
                                center_of_mass['pos_y'].rename('center_y'),
                                distances_with_time['delta']], axis=1).dropna()
        time_greater_than = y_position[y_position['car_y'] > y_position['center_y']]['delta'].sum()
        time_less_than = y_position[y_position['car_y'] < y_position['center_y']]['delta'].sum()
        if player.is_orange:
            player.stats.relative_positioning.time_behind_center_of_mass = time_greater_than
            player.stats.relative_positioning.time_in_front_of_center_of_mass = time_less_than
        else:
            player.stats.relative_positioning.time_behind_center_of_mass = time_less_than
            player.stats.relative_positioning.time_in_front_of_center_of_mass = time_greater_than
