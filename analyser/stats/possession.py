import pandas as pd
from typing import Dict

from json_parser.game import Game
from json_parser.player import Player
from json_parser.team import Team


class PossessionStat:
    def __init__(self, team_possessions: Dict[Team, float], player_possessions: Dict[Player, float]):
        self.team_possessions = team_possessions
        self.player_possessions = player_possessions

    @classmethod
    def get_possession(cls, game: Game) -> 'PossessionStat':
        team_possessions = cls.get_team_possessions(game)
        player_possessions = cls.get_player_possessions(game)
        return cls(team_possessions, player_possessions)

    @staticmethod
    def get_team_possessions(game: Game) -> Dict[Team, float]:
        frame_possession_time_deltas = pd.concat(
            [
                game.ball.hit_team_no,
                game.frames.delta
            ],
            axis=1
        )
        last_hit_possession = frame_possession_time_deltas.groupby('hit_team_no').sum()
        team_possessions = {
            team: last_hit_possession.delta.loc[team.is_orange] for team in game.teams
        }
        return team_possessions

    @staticmethod
    def get_player_possessions(game: Game) -> Dict[Player, float]:
        player_possessions = {
            player: 0 for player in game.players
        }
        frame_possession_time_deltas = pd.concat(
            [
                game.ball.hit_team_no,
                game.frames.delta
            ],
            axis=1
        )
        hits = sorted(game.hits.items())
        hit_number = 0
        for hit_frame_number, hit in hits:
            try:
                next_hit_frame_number = hits[hit_number + 1][0]
            except IndexError:
                # last hit
                next_hit_frame_number = game.goals[-1].frame_number

            hit_possession_time = frame_possession_time_deltas[
                                      frame_possession_time_deltas.hit_team_no == hit.player.is_orange
                                      ].delta.loc[
                                  hit_frame_number:next_hit_frame_number
                                  ].sum()
            player_possessions[hit.player] += hit_possession_time
            hit_number += 1

        return player_possessions