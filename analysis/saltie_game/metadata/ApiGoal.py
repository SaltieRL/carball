class ApiGoal:
    def __init__(self, player_name: str = None, frame: int = None):
        self.player_name = player_name
        self.frame = frame

    def __str__(self):
        return 'Goal by %s on frame %s' % (self.player_name, self.frame)

    @staticmethod
    def create_goals_from_game(game):
        return [ApiGoal(goal.player_name, goal.frame_number) for goal in game.goals]
