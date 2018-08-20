from ..analysis.saltie_game.metadata.ApiPlayer import ApiPlayer
from ..analysis.saltie_game.metadata.ApiGame import ApiGame
from ..json_parser.game import Game
from ..generated.api import game_pb2

import logging

logger = logging.getLogger(__name__)


class AnalysisManager:

    def create_analysis(self, game: Game):
        logger.info("Creating SaltieGame from %s" % game)
        protobuf_game = game_pb2.Game()
        self.get_game_metadata(game, protobuf_game)
        print(protobuf_game)

    def get_game_metadata(self, game: Game, proto_game: game_pb2.Game):
        id_creator = self.create_player_id_function(game)
        ApiGame.create_from_game(proto_game.game_metadata, game, id_creator)
        for player in game.players:
            player_proto = proto_game.players.add()
            ApiPlayer.create_from_player(player_proto, player, id_creator)

    def create_player_id_function(self, game: Game):
        name_map = dict()
        for player in game.players:
            name_map[player.name] = player.online_id

        def create_name(proto_player_id, name):
            proto_player_id.id = name_map[name]

        return create_name
