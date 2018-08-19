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

    def __str__(self):
        colour = 'orange' if self.is_orange else 'blue'
        if self.name is not None:
            return 'Team: %s (Goals: %s) on %s: (%s players)' % (self.name, self.score, colour, len(self.players))
        else:
            return 'Team on %s with %s goals: (%s players)' % (colour, self.score, len(self.players))

    @staticmethod
    def create_teams_from_game(game):
        teams = []
        for team in game.teams:
            players = [ApiPlayer.create_from_player(player) for player in team.players]
            teams.append(ApiTeam(team.name, players, team.score, team.is_orange))
        return teams
