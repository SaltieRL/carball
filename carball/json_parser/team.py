import logging

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .player import Player

logger = logging.getLogger(__name__)


class Team:
    def __init__(self):
        self.is_orange = None
        self.name = None
        self.score = None
        self.actor_id = None

        self.players = set()

    def __repr__(self):
        if self.is_orange is not None:
            team_colour = 'Orange' if self.is_orange else 'Blue'
        else:
            team_colour = 'None'
        if self.name:
            return '%s: %s (%s)' % (self.__class__.__name__, self.name, team_colour)
        else:
            return '%s: %s' % (self.__class__.__name__, team_colour)

    def parse_team_data(self, team_data: dict):
        self.name = team_data.get("TAGame.Team_TA:CustomTeamName", None)
        self.is_orange = team_data['TypeName'].endswith('1')
        self.score = team_data.get("Engine.TeamInfo:Score", 0)  # RLCS S4 05E1F21043CCFCC442DCEC8B544A768F
        self.actor_id = team_data["Id"]

        logger.info('Created Team from stats: %s' % self)
        return self

    def add_player(self, player: 'Player'):
        self.players.add(player)
        player.team = self
