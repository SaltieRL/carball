from .base import *


class GameEventHandler(BaseActorHandler):
    type_name = 'Archetypes.GameEvent.GameEvent_Soccar'

    @classmethod
    def can_handle(cls, actor):
        return actor['ClassName'].startswith('TAGame.GameEvent_Soccar_TA')

    def update(self, actor, frame_number, time, delta):
        self.parser.soccar_game_event_actor = actor
        frame_data = {
            'time': time,
            'delta': delta,
            'seconds_remaining': actor.get('TAGame.GameEvent_Soccar_TA:SecondsRemaining', None),
            'replicated_seconds_remaining': actor.get('TAGame.GameEvent_TA:ReplicatedGameStateTimeRemaining', None),
            'is_overtime': actor.get('TAGame.GameEvent_Soccar_TA:bOverTime', None),
            'ball_has_been_hit': actor.get('TAGame.GameEvent_Soccar_TA:bBallHasBeenHit', None)
        }
        self.parser.frames_data[frame_number] = frame_data
