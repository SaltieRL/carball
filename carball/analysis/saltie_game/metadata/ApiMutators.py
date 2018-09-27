from typing import Callable

from ....json_parser.game import Game
from ....generated.api.metadata import mutators_pb2

class ApiMutators:
    @staticmethod
    def create_from_game(proto_mutators: mutators_pb2.Mutators,
                        game: Game, id_creator: Callable) -> mutators_pb2.Mutators:
        proto_mutators.ball_type = game.ball_type
        proto_mutators.game_mutator_index = game.game_info.mutator_index

        return id_creator, proto_mutators
        