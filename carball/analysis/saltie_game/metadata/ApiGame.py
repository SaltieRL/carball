from typing import Callable

from carball.generated.api import party_pb2
from ....json_parser.game import Game
from ....generated.api.metadata import game_metadata_pb2
from .ApiDemo import ApiDemo
from .ApiGoal import ApiGoal


class ApiGameScore:
    @staticmethod
    def create_from_game(game):
        game_score = game_metadata_pb2.GameScore()
        for team in game.teams:
            if team.is_orange:
                game_score.team_1_score = team.score
            else:
                game_score.team_0_score = team.score
        return game_score


class ApiGame:
    @staticmethod
    def create_from_game(proto_game: game_metadata_pb2.GameMetadata,
                         game: Game, id_creator: Callable) -> game_metadata_pb2.GameMetadata:
        proto_game.id = game.id
        proto_game.name = str(game.name)
        proto_game.map = game.map
        if game.replay_version is not None:
            proto_game.version = game.replay_version
        proto_game.time = int(game.datetime.timestamp())
        proto_game.frames = game.frames.index.max()
        proto_game.score.CopyFrom(ApiGameScore.create_from_game(game))
        ApiGoal.create_goals_from_game(game, proto_game.goals, id_creator)
        ApiDemo.create_demos_from_game(game, proto_game.demos, id_creator)
        if game.primary_player is not None and game.primary_player['id'] is not None:
            proto_game.primary_player.id = game.primary_player['id']
        return id_creator, proto_game

    @staticmethod
    def create_parties(parties, game: Game, id_creator: Callable):
        for k, v in game.parties.items():
            proto_party: party_pb2.Party = parties.add()
            proto_party.leader_id.id = k
            for p in v:
                player = proto_party.members.add()
                player.id = p
