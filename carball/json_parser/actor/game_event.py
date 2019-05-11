from .base import *


class GameEventHandler(BaseActorHandler):
    type_name = 'Archetypes.GameEvent.GameEvent_Soccar'

    @classmethod
    def can_handle(cls, actor):
        return actor['ClassName'].startswith('TAGame.GameEvent_Soccar_TA')

    def update(self, actor, time, delta):
        self.parser.soccar_game_event_actor = actor
        frame_data = self.parser.frame_data['frames_data']
        frame_data['seconds_remaining'] = actor.get('TAGame.GameEvent_Soccar_TA:SecondsRemaining', None)
        frame_data['replicated_seconds_remaining'] = \
            actor.get('TAGame.GameEvent_TA:ReplicatedGameStateTimeRemaining', None)
        frame_data['is_overtime'] = actor.get('TAGame.GameEvent_Soccar_TA:bOverTime', None)
        frame_data['ball_has_been_hit'] = actor.get('TAGame.GameEvent_Soccar_TA:bBallHasBeenHit', None)
