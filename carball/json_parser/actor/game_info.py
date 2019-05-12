from .base import *


class GameInfoHandler(BaseActorHandler):
    priority = 1

    @classmethod
    def can_handle(cls, actor):
        return actor['TypeName'].endswith(':GameReplicationInfoArchetype')

    def update(self, actor, frame_number, time, delta):
        if self.parser.game_info_actor is None:
            self.parser.game_info_actor = actor
