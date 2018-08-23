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
        proto_game.name = str(game.name)
        proto_game.map = game.map
        if game.replay_version is not None:
            proto_game.version = game.replay_version
        proto_game.time = int(time.mktime(game.datetime.timetuple())*1e3 + game.datetime.microsecond/1e3)
        proto_game.frames = game.frames.index.max()
        proto_game.score.CopyFrom(ApiGameScore.create_from_game(game))
        ApiGoal.create_goals_from_game(game, proto_game.goals, id_creator)
        ApiDemo.create_demos_from_game(game, proto_game.demos, id_creator)
        return id_creator, proto_game
