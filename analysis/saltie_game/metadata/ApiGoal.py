class ApiGoal:
    def __init__(self, player_name: str = None, frame: int = None):
        self.player_name = player_name
        self.frame = frame

    @staticmethod
    def create_goals_from_game(game):
        return [ApiGoal(goal.player_name, goal.frame_number) for goal in game.goals]
