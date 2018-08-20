from typing import List, Callable

from ....generated.api.metadata import game_metadata_pb2
from ....json_parser.game import Game


class ApiGoal:
    @staticmethod
    def create_goals_from_game(game: Game, id_creator: Callable) -> List[game_metadata_pb2.Goal]:
        goals = []
        for goal in game.goals:
            proto_goal = game_metadata_pb2.Goal()
            proto_goal.frame = goal.frame_number
            id_creator(proto_goal.player_id, goal.player_name)
            goals.append(proto_goal)
        return goals
