from typing import List

from .ApiPlayer import ApiPlayer


class ApiTeam:

    def __init__(self, name: str = None, players: List[ApiPlayer] = None,
                 score: int = None, is_orange: bool = None
                 ):
        self.name = name
        self.players = players
        self.score = score
        self.is_orange = is_orange

    @staticmethod
    def create_teams_from_game(game):
        teams = []
        for team in game.teams:
            players = [ApiPlayer.create_from_player(player) for player in team.players]
            teams.append(ApiTeam(team.name, players, team.score, team.is_orange))
        return teams
