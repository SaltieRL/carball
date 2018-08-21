from typing import Dict

from replay_analysis.analysis.hit_detection.base_hit import BaseHit
from replay_analysis.analysis.saltie_game.saltie_hit import SaltieHit
from replay_analysis.generated.api.player_pb2 import Player
from ..analysis.saltie_game.saltie_game import SaltieGame
from ..analysis.saltie_game.metadata.ApiPlayer import ApiPlayer
from ..analysis.saltie_game.metadata.ApiGame import ApiGame
from ..json_parser.game import Game
from ..generated.api import game_pb2

import logging

logger = logging.getLogger(__name__)


class AnalysisManager:

    id_creator = None

    def create_analysis(self, game: Game):
        logger.info("Creating SaltieGame from %s" % game)
        protobuf_game = game_pb2.Game()
        self.id_creator = self.create_player_id_function(game)
        player_map = self.get_game_metadata(game, protobuf_game)
        data_frames, kickoff_frames = self.get_frames(game, protobuf_game)
        self.get_extra_stats(game, protobuf_game, player_map, data_frames, kickoff_frames)
        print(protobuf_game)

    def get_game_metadata(self, game: Game, proto_game: game_pb2.Game) -> Dict[str, Player]:

        ApiGame.create_from_game(proto_game.game_metadata, game, self.id_creator)
        player_map = dict()
        for player in game.players:
            player_proto = proto_game.players.add()
            ApiPlayer.create_from_player(player_proto, player, self.id_creator)
            player_map[player.online_id] = player_proto
        return player_map

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
        # proto_game.kickoff_frames = self.write_pandas_to_memeory(kickoff_frames)
        return data_frame, kickoff_frames

    def write_pandas_to_memeory(self, dataframe):
        return None

    def get_extra_stats(self, game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player],
                        data_frames, kickoff_frames):
        hits = BaseHit.get_hits_from_game(game, proto_game, self.id_creator)
        logger.info("Found %s hits." % len(hits))

        SaltieHit.get_saltie_hits_from_game(game, proto_game, hits, player_map,
                                            data_frames, kickoff_frames)
        logger.info("Analysed hits.")

        # self.stats = get_stats(self)

