from typing import Callable

from ....json_parser.game import Game


class ApiGoal:
    @staticmethod
    def create_goals_from_game(game: Game, proto_goal_list, id_creator: Callable):
        for goal in game.goals:
            proto_goal = proto_goal_list.add()
            proto_goal.frame_number = goal.frame_number
            id_creator(proto_goal.player_id, goal.player_name)
