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
    def can_handle(cls, actor: dict) -> bool:
        return actor['TypeName'].startswith('Archetypes.Ball.')

    def update(self, actor: dict, frame_number: int, time: float, delta: float) -> None:
        if actor.get('TAGame.RBActor_TA:bIgnoreSyncing', False):
            return

        if self.parser.game.ball_type is None:
            self.parser.game.ball_type = BALL_TYPES.get(actor['TypeName'], mutators.DEFAULT)

        ball_data = BallActor.get_data_dict(actor, self.parser.replay_version)
        self.parser.ball_data[frame_number] = ball_data

        if self.parser.game.ball_type == mutators.BREAKOUT:
            damage_index = actor.get('TAGame.Ball_Breakout_TA:DamageIndex', 0)
            if damage_index > self.parser.dropshot['ball_state']:
                team = actor.get('TAGame.Ball_Breakout_TA:LastTeamTouch')
                self.parser.dropshot['ball_events'].append({
                    'state': damage_index,
                    'frame_number': frame_number,
                    'team': team
                })
            self.parser.dropshot['ball_state'] = damage_index
            self.parser.ball_data[frame_number]['dropshot_phase'] = damage_index
