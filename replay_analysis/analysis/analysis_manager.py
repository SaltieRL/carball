from ..analysis.saltie_game.saltie_game import SaltieGame
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
        self.get_frames(game, protobuf_game)
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

    def get_frames(self, game: Game, proto_game: game_pb2.Game):
        data_frame = SaltieGame.create_data_df(game)
        kickoff_frames = SaltieGame.get_kickoff_frames(game)
        for goal_number, goal in enumerate(game.goals):
            data_frame.loc[
                kickoff_frames[goal_number]: goal.frame_number, ('game', 'goal_number')
            ] = goal_number

        # Set goal_number of frames that are post-last-goal to -1 (ie non None)
        if len(kickoff_frames) > len(proto_game.game_metadata.goals):
            data_frame.loc[kickoff_frames[-1]:, ('game', 'goal_number')] = -1

        logger.info("Assigned goal_number in .data_frame")
        proto_game.kickoff_frames = self.write_pandas_to_memeory(kickoff_frames)
        return data_frame

    def write_pandas_to_memeory(self, dataframe):
        return None

