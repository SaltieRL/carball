from .base import *


class GameEventHandler(BaseActorHandler):

    @classmethod
    def can_handle(cls, actor: dict) -> bool:
        if actor['ClassName'] is not None:
            return actor['ClassName'].startswith('TAGame.GameEvent_Soccar_TA') or actor['ClassName'].startswith('TAGame.GameEvent_GodBall_TA')
        else:
            return False

    def update(self, actor: dict, frame_number: int, time: float, delta: float) -> None:
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
