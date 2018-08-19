import datetime
import json
from typing import List

from ....json_parser.game import Game
from .ApiDemo import ApiDemo
from .ApiGoal import ApiGoal
from .ApiTeam import ApiTeam


class ApiGameScore:
    def __init__(self, team0score: int = None, team1score: int = None):
        self.team0score = team0score
        self.team1score = team1score

    def __str__(self):
        return '(Blue) %s vs %s (Orange)' % (self.team0score, self.team1score)

    @staticmethod
    def create_from_game(game):
        team_0_score = None
        team_1_score = None
        for team in game.teams:
            if team.is_orange:
                team_1_score = team.score
            else:
                team_0_score = team.score
        return ApiGameScore(team_0_score, team_1_score)


class ApiGame:
    def __init__(self,
                 id: str = None,
                 name: str = None,
                 map_: str = None,
                 version: int = None,
                 time: datetime.datetime = None,
                 frames: int = None,
                 score: ApiGameScore = None,
                 teams: List[ApiTeam] = None,
                 goals: List[ApiGoal] = None,
                 demos: List[ApiDemo] = None,
                 ):
        self.id = id
        self.name = name
        self.map = map_
        self.version = version
        self.time = time
        self.frames = frames
        self.score = score
        self.teams = teams
        self.goals = goals
        self.demos = demos

    @staticmethod
    def create_from_game(game: Game):
        return ApiGame(
            id=game.id,
            name=game.name,
            map_=game.map,
            version=game.replay_version,
            time=game.datetime,
            frames=game.frames.index.max(),
            score=ApiGameScore.create_from_game(game),
            teams=ApiTeam.create_teams_from_game(game),
            goals=ApiGoal.create_goals_from_game(game),
            demos=ApiDemo.create_demos_from_game(game)
        )

    def to_json(self) -> str:
        # TODO: Check if this handles ApiGame.time conversion.
        return json.dumps(self, default=lambda o: getattr(o, '__dict__', str(o)))


if __name__ == '__main__':
    import os
    import pickle

    base_dir = os.path.dirname(os.path.dirname(__file__))
    print(base_dir)
    with open(os.path.join(base_dir, 'parsed', "7.replay.pkl"), 'rb') as f:
        pickled_game = pickle.load(f)
        print(pickled_game)

    api_game = ApiGame.create_from_game(pickled_game)
    json_api_game = api_game.to_json()
    with open('x.json', 'w') as f:
        f.write(json_api_game)
