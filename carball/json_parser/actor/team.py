from .ball import *


class TeamHandler(BaseActorHandler):

    @classmethod
    def can_handle(cls, actor: dict) -> bool:
        return actor['ClassName'] == 'TAGame.Team_Soccar_TA'

    def update(self, actor: dict, frame_number: int, time: float, delta: float) -> None:
        self.parser.team_dicts[actor['Id']] = actor
        self.parser.team_dicts[actor['Id']]['colour'] = 'blue' if actor["TypeName"] == "Archetypes.Teams.Team0" else \
            'orange'
