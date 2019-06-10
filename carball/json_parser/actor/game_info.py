from .base import *


class GameInfoHandler(BaseActorHandler):

    @classmethod
    def can_handle(cls, actor: dict) -> bool:
        return actor['TypeName'].endswith(':GameReplicationInfoArchetype')

    def update(self, actor: dict, frame_number: int, time: float, delta: float) -> None:
        if self.parser.game_info_actor is None:
            self.parser.game_info_actor = actor
