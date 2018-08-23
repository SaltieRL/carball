from typing import Dict

import pandas as pd

from replay_analysis.analysis.stats.stats import BaseStat, HitStat
from replay_analysis.generated.api import game_pb2
from replay_analysis.generated.api.player_pb2 import Player
from replay_analysis.generated.api.stats.events_pb2 import Hit
from replay_analysis.generated.api.stats.team_stats_pb2 import TeamStats
from replay_analysis.json_parser.game import Game


class PossessionStat(BaseStat, HitStat):

    frame_possession_time_deltas = None

    def calculate_team_stat(self, team_stat_list: Dict[int, TeamStats], game: Game,
                            proto_game: game_pb2.Game, player_map: Dict[str, Player],
                            data_frames):
        goal_frames = data_frames.game.goal_number.notnull()
        dataframe = data_frames[goal_frames]
        frame_possession_time_deltas = pd.concat(
            [
                dataframe['ball', 'hit_team_no'],
                dataframe['game', 'delta']
            ],
            axis=1
        )
        frame_possession_time_deltas.columns = ['hit_team_no', 'delta']

        last_hit_possession = frame_possession_time_deltas.groupby('hit_team_no').sum()

        for index, stat in team_stat_list.items():
            stat.possession.possession_time = float(last_hit_possession.delta.loc[index])

    """
    @staticmethod
    def get_player_possessions(saltie_game: 'SaltieGame') -> Dict[str, float]:
        player_possessions: Dict[str, float] = {
            player.name: 0 for team in saltie_game.api_game.teams for player in team.players
        }

        goal_frames = saltie_game.data_frame.game.goal_number.notnull()
        dataframe = saltie_game.data_frame[goal_frames]
        frame_possession_time_deltas = pd.concat(
            [
                dataframe['ball', 'hit_team_no'],
                dataframe['game', 'delta']
            ],
            axis=1
        )
        frame_possession_time_deltas.columns = ['hit_team_no', 'delta']

        hits = sorted(saltie_game.hits.items())
        hit_number = 0
        for hit_frame_number, hit in hits:
            try:
                next_hit_frame_number = hits[hit_number + 1][0]
            except IndexError:
                # last hit
                next_hit_frame_number = saltie_game.api_game.goals[-1].frame

            hit_possession_time = frame_possession_time_deltas[
                                      frame_possession_time_deltas.hit_team_no == hit.player.is_orange
                                      ].delta.loc[hit_frame_number:next_hit_frame_number].sum()
            player_possessions[hit.player.name] += hit_possession_time
            hit_number += 1

        return player_possessions
    """

    def initialize_hit_stat(self, game: Game, player_map: Dict[str, Player], data_frames):
        goal_frames = data_frames.game.goal_number.notnull()
        dataframe = data_frames[goal_frames]
        self.frame_possession_time_deltas = pd.concat(
            [
                dataframe['ball', 'hit_team_no'],
                dataframe['game', 'delta']
            ],
            axis=1
        )
        self.frame_possession_time_deltas.columns = ['hit_team_no', 'delta']

    def calculate_next_hit_stat(self, game: Game, proto_game: game_pb2.Game, saltie_hit: Hit, next_saltie_hit: Hit,
                                player_map: Dict[str, Player]):
        player = player_map[saltie_hit.player_id.id]
        next_player = player_map[next_saltie_hit.player_id.id]
        if player.is_orange == next_player.is_orange:
            hit_possession_time = self.frame_possession_time_deltas.delta.loc[
                                  saltie_hit.frame_number:next_saltie_hit.frame_number].sum()
            player.stats.possession.possession_time = player.stats.possession.possession_time + hit_possession_time
        else:
            hit_possession_time = self.frame_possession_time_deltas.delta.loc[
                                  saltie_hit.frame_number:next_saltie_hit.frame_number].sum()
            player.stats.possession.possession_time = player.stats.possession.possession_time + hit_possession_time
            proto_game.game_stats.neutral_possession_time = proto_game.game_stats.neutral_possession_time + hit_possession_time
