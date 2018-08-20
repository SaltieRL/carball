from typing import Callable
import time

from ....json_parser.game import Game
from ....generated.api.metadata import game_metadata_pb2
from .ApiDemo import ApiDemo
from .ApiGoal import ApiGoal
from .ApiTeam import ApiTeam


class ApiGameScore:
    @staticmethod
    def create_from_game(game):
        gamescore = game_metadata_pb2.GameScore()
        for team in game.teams:
            if team.is_orange:
                gamescore.team_1_score = team.score
            else:
                gamescore.team_0_score = team.score
        return gamescore


class ApiGame:
    @staticmethod
    def create_from_game(proto_game: game_metadata_pb2.GameMetadata, game: Game, id_creator: Callable) -> game_metadata_pb2.GameMetadata:
        proto_game.id = game.id
        proto_game.name = game.name
        proto_game.map = game.map
        proto_game.version = game.replay_version
        proto_game.time = int(time.mktime(game.datetime.timetuple())*1e3 + game.datetime.microsecond/1e3)
        proto_game.frames = game.frames.index.max()
        proto_game.score.CopyFrom(ApiGameScore.create_from_game(game))
        proto_game.teams.extend(ApiTeam.create_teams_from_game(game, id_creator))
        proto_game.goals.extend(ApiGoal.create_goals_from_game(game, id_creator))
        proto_game.demos.extend(ApiDemo.create_demos_from_game(game, id_creator))
        return id_creator, proto_game