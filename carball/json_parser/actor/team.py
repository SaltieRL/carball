from .ball import *


class TeamHandler(BaseActorHandler):

    @classmethod
    def can_handle(cls, actor):
        return actor['ClassName'] == 'TAGame.Team_Soccar_TA'

    def update(self, actor, time, delta):
        self.parser.team_dicts[actor['Id']] = actor
        self.parser.team_dicts[actor['Id']]['colour'] = 'blue' if actor["TypeName"] == "Archetypes.Teams.Team0" else \
            'orange'
