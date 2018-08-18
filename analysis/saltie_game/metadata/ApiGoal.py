# noinspection PyPep8Naming
class ApiGoal:
    def __init__(self, playerName: str = None, frame: int = None):
        self.player_name = playerName
        self.frame = frame

    @staticmethod
    def create_goals_from_game(game):
        return [ApiGoal(goal.player_name, goal.frame_number) for goal in game.goals]
