from typing import Callable

from ....json_parser.game import Game


class ApiDemo:
    @staticmethod
    def create_demos_from_game(game: Game, proto_demo_list, id_creator: Callable):
        for demo in game.demos:
            proto_demo = proto_demo_list.add()
            proto_demo.frame_number = demo['frame_number']
            id_creator(proto_demo.attacker_id, demo['attacker'].name)
            id_creator(proto_demo.victim_id, demo['victim'].name)
