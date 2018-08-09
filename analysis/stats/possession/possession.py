from typing import Dict, TYPE_CHECKING, List, Tuple

import pandas as pd

from analysis.hit_detection.base_hit import BaseHit
from json_parser.player import Player
from json_parser.team import Team

if TYPE_CHECKING:
    from ...saltie_game.saltie_game import SaltieGame


class PossessionStat:
    def __init__(self, team_possessions: Dict[Team, float], player_possessions: Dict[Player, float]):
        self.team_possessions = team_possessions
        self.player_possessions = player_possessions

    @classmethod
    def get_possession(cls, saltie_game: 'SaltieGame') -> 'PossessionStat':
        team_possessions = cls.get_team_possessions(saltie_game)
        player_possessions = cls.get_player_possessions(saltie_game)
        return cls(team_possessions, player_possessions)

    @staticmethod
    def get_team_possessions(saltie_game: 'SaltieGame') -> Dict[Team, float]:
        frame_possession_time_deltas = pd.concat(
            [
                saltie_game.data_frame['ball', 'hit_team_no'],
                saltie_game.data_frame.delta
            ],
            axis=1
        )
        frame_possession_time_deltas.columns = ['hit_team_no', 'delta']

        last_hit_possession = frame_possession_time_deltas.groupby('hit_team_no').sum()
        team_possessions = {
            int(team.isOrange): last_hit_possession.delta.loc[int(team.isOrange)] for team in saltie_game.api_game.teams
        }
        return team_possessions

    @staticmethod
    def get_player_possessions(saltie_game: 'SaltieGame') -> Dict[Player, float]:
        player_possessions = {
            player.name: 0 for team in saltie_game.api_game.teams for player in team.players
        }
        frame_possession_time_deltas = pd.concat(
            [
                saltie_game.data_frame['ball', 'hit_team_no'],
                saltie_game.data_frame.delta
            ],
            axis=1
        )
        frame_possession_time_deltas.columns = ['hit_team_no', 'delta']

        hits: List[Tuple[int, 'BaseHit']] = sorted(saltie_game.hits.items())
        hit_number = 0
        for hit_frame_number, hit in hits:
            try:
                next_hit_frame_number = hits[hit_number + 1][0]
            except IndexError:
                # last hit
                next_hit_frame_number = saltie_game.api_game.goals[-1].frame

            hit_possession_time = frame_possession_time_deltas[
                                      frame_possession_time_deltas.hit_team_no == hit.player.is_orange
                                      ].delta.loc[
                                  hit_frame_number:next_hit_frame_number
                                  ].sum()
            player_possessions[hit.player.name] += hit_possession_time
            hit_number += 1

        return player_possessions
