class Goal:

    def __init__(self, goal_dict, game):
        self.time = goal_dict["Time"]
        self.player_name = goal_dict["PlayerName"]
        self.player_team = goal_dict["PlayerTeam"]

        self.player = self.get_player(game)
        self.frame_number = self.get_frame_number(game)

    def __repr__(self):
        return "Goal by %s on frame %s" % (self.player.name, self.frame_number)

    def get_player(self, game):
        for player in game.players:
            if player.name == self.player_name:
                return player

    def get_frame_number(self, game):
        for frame_number, frame in enumerate(game.replay_data):
            frame_time = frame["Time"]
            if frame_time > self.time:
                return frame_number