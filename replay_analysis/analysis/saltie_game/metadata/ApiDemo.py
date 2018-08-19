from typing import List, Callable

from ....generated.api.metadata import game_metadata_pb2
from ....json_parser.game import Game


class ApiDemo:
    @staticmethod
    def create_demos_from_game(game: Game, id_creator: Callable) -> List[game_metadata_pb2.Demo]:
        demos = []
        for demo in game.demos:
            proto_demo = game_metadata_pb2.Demo()
            proto_demo.frame = demo['frame_number']
            proto_demo.attacker = id_creator(demo['attacker'])
            proto_demo.victim = id_creator(demo['victim'])
            demos.append(proto_demo)
        return demos
