from typing import Dict

import pandas as pd

from carball.analysis.constants.playlist import get_team_size_from_game
from carball.analysis.stats.utils.pandas_utils import sum_deltas_by_player_name
from carball.generated.api.player_pb2 import Player

from carball.generated.api import game_pb2
from carball.json_parser.game import Game

from carball.generated.api.stats.team_stats_pb2 import TeamStats

from carball.analysis.stats.tendencies.team_tendencies import TeamTendencies


class RelativeTendencies(TeamTendencies):
    def calculate_team_stat(self, team_stat_list: Dict[int, TeamStats], game: Game, proto_game: game_pb2.Game,
                            player_map: Dict[str, Player], data_frame: pd.DataFrame):
        for team in proto_game.teams:
            team_size = get_team_size_from_game(proto_game)
            if len(team.player_ids) <= 2 or team_size <= 2:
                # center of mass does not matter for 1s games
                continue

            player_y = {player_map[player_id.id].name: data_frame[player_map[player_id.id].name].pos_y
                        for player_id in team.player_ids}

            player_y_data_frame = pd.concat(player_y, axis=1)
            last_person = player_y_data_frame.idxmin(axis=1).rename('last_person')
            first_person = player_y_data_frame.idxmax(axis=1).rename('first_person')

            position_distances_time = pd.concat([
                sum_deltas_by_player_name(data_frame, players_data_frame)
                for players_data_frame in [last_person, first_person]
            ], axis=1)

            position_distances_time.fillna(value=0, inplace=True)

            for player_id in team.player_ids:
                relative_position = player_map[player_id.id].stats.relative_positioning
                player_name = player_map[player_id.id].name
                try:
                    # flip first and last if you are orange
                    if team.is_orange:
                        relative_position.time_most_back_player = position_distances_time['first_person'][player_name]
                        relative_position.time_most_forward_player = position_distances_time['last_person'][player_name]
                    else:
                        relative_position.time_most_back_player = position_distances_time['last_person'][player_name]
                        relative_position.time_most_forward_player = position_distances_time['first_person'][player_name]

                    total_time = relative_position.time_most_back_player + relative_position.time_most_forward_player
                    relative_position.time_between_players = player_map[player_id.id].time_in_game - total_time
                except (AttributeError, KeyError) as e:
                    pass
