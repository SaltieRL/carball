from .base import *
from carball.generated.api.game_pb2 import mutators_pb2 as mutators
from carball.json_parser.actor_parsing import BallActor

BALL_TYPES = {
    'Archetypes.Ball.Ball_Default': mutators.DEFAULT,
    'Archetypes.Ball.Ball_Basketball': mutators.BASKETBALL,
    'Archetypes.Ball.Ball_Puck': mutators.PUCK,
    'Archetypes.Ball.CubeBall': mutators.CUBEBALL,
    'Archetypes.Ball.Ball_Breakout': mutators.BREAKOUT
}


class BallHandler(BaseActorHandler):

    @classmethod
    def can_handle(cls, actor):
        return actor['TypeName'].startswith('Archetypes.Ball.')

    def update(self, actor, frame_number, time, delta):
        if actor.get('TAGame.RBActor_TA:bIgnoreSyncing', False):
            self.parser.frame_data['ball_data']['ball'].clear()
            return

        if self.parser.game.ball_type is None:
            self.parser.game.ball_type = BALL_TYPES.get(actor['TypeName'], mutators.DEFAULT)

        ball_data = BallActor.get_data_dict(actor, self.parser.replay_version)
        self.parser.frame_data['ball_data'] = ball_data
