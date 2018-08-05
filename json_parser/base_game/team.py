import logging

logger = logging.getLogger(__name__)


class Team:

    def __init__(self):
        self.is_orange = None
        self.name = None
        self.score = None
        self.players = set()
        logger.info('Created Team: %s' % self)

    def __repr__(self):
        if self.is_orange is not None:
            team_colour = 'Orange' if self.is_orange else 'Blue'
        else:
            team_colour = 'None'
        if self.name:
            return '%s: %s (%s)' % (self.__class__.__name__, self.name, team_colour)
        else:
            return '%s: %s' % (self.__class__.__name__,  team_colour)


    def parse_team_data(self, team_data):
        self.name = team_data.get("TAGame.Team_TA:CustomTeamName", None)
        self.is_orange = team_data['TypeName'].endswith('1')
        self.score = team_data.get("Engine.TeamInfo:Score", 0)  # RLCS S4 05E1F21043CCFCC442DCEC8B544A768F
        self.actor_id = team_data["Id"]
        return self

    def add_player(self, player):
        self.players.add(player)
        player.team = self