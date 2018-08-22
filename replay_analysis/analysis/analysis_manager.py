import time
from typing import Dict
import logging

from replay_analysis.analysis.hit_detection.base_hit import BaseHit
from replay_analysis.analysis.saltie_game.metadata.ApiTeam import ApiTeam
from replay_analysis.analysis.saltie_game.saltie_hit import SaltieHit
from replay_analysis.analysis.stats.pandas_manager import PandasManager
from replay_analysis.analysis.stats.stats_manager import StatsManager
from replay_analysis.generated.api.player_pb2 import Player
from replay_analysis.generated.api.stats import data_frames_pb2
from ..analysis.saltie_game.saltie_game import SaltieGame
from ..analysis.saltie_game.metadata.ApiPlayer import ApiPlayer
from ..analysis.saltie_game.metadata.ApiGame import ApiGame
from ..json_parser.game import Game
from ..generated.api import game_pb2

logger = logging.getLogger(__name__)


class AnalysisManager:

    id_creator = None
    timer = None

    def __init__(self, game: Game):
        self.game = game
        self.protobuf_game = game_pb2.Game()
        self.id_creator = self.create_player_id_function(game)
        self.stats_manager = StatsManager()

    def create_analysis(self):
        self.start_time()
        player_map = self.get_game_metadata(self.game, self.protobuf_game)
        self.log_time("creating metadata")
        data_frames, kickoff_frames = self.get_frames(self.game, self.protobuf_game)
        self.log_time("getting frames")
        self.calculate_hit_stats(self.game, self.protobuf_game, player_map, data_frames, kickoff_frames)
        self.log_time("calculating hits")
        self.get_advanced_stats(self.game, self.protobuf_game, player_map, data_frames, kickoff_frames)

        self.store_frames(data_frames)
        # logger.debug(self.protobuf_game)

    def get_game_metadata(self, game: Game, proto_game: game_pb2.Game) -> Dict[str, Player]:

        # create general metadata
        ApiGame.create_from_game(proto_game.game_metadata, game, self.id_creator)

        # create team metadata
        proto_game.teams.extend(ApiTeam.create_teams_from_game(game, self.id_creator))

        # create player metadata
        player_map = dict()
        for player in game.players:
            player_proto = proto_game.players.add()
            ApiPlayer.create_from_player(player_proto, player, self.id_creator)
            player_map[player.online_id] = player_proto

        return player_map

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



    def calculate_hit_stats(self, game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player],
                            data_frames, kickoff_frames):
        logger.info("Looking for hits.")
        hits = BaseHit.get_hits_from_game(game, proto_game, self.id_creator, data_frames)
        logger.info("Found %s hits." % len(hits))

        SaltieHit.get_saltie_hits_from_game(game, proto_game, hits, player_map,
                                            data_frames, kickoff_frames)
        logger.info("Analysed hits.")

        # self.stats = get_stats(self)

    def start_time(self):
        self.timer = time.time()
        logger.info("starting timer")

    def log_time(self, message=""):
        end = time.time()
        logger.info("Time taken for %s is %s milliseconds", message, (end - self.timer) * 1000)
        self.timer = end

    def create_player_id_function(self, game: Game):
        name_map = dict()
        for player in game.players:
            name_map[player.name] = player.online_id

        def create_name(proto_player_id, name):
            proto_player_id.id = name_map[name]

        return create_name

    def get_advanced_stats(self, game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player],
                           data_frames, kickoff_frames):
        self.stats_manager.get_stats(game, proto_game, player_map, data_frames, kickoff_frames)

    def store_frames(self, data_frames):
        frame_proto = data_frames_pb2.DataFrames()
        PandasManager.add_pandas(frame_proto, data_frames)
        self.protobuf_game.Extensions[game_pb2.data_frames] = frame_proto

