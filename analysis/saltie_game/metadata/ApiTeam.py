from typing import List

from .ApiPlayer import ApiPlayer


# noinspection PyPep8Naming
class ApiTeam:

    def __init__(self, name: str = None, players: List[ApiPlayer] = None,
                 score: int = None, isOrange: bool = None
                 ):
        self.name = name
        self.players = players
        self.score = score
        self.is_orange = isOrange

    @staticmethod
    def create_teams_from_game(game):
        teams = []
        for team in game.teams:
            players = [ApiPlayer.create_from_player(player) for player in team.players]
            teams.append(ApiTeam(team.name, players, team.score, team.is_orange))
        return teams
