import logging
from typing import Dict, Callable

from ..analysis.hit_detection.base_hit import BaseHit
from ..analysis.hit_detection.hit_analysis import SaltieHit
from ..generated.api import game_pb2
from ..json_parser.game import Game
from ..generated.api.player_pb2 import Player

logger = logging.getLogger(__name__)


class EventsCreator:
    """
        Handles the creation of all events that can then be later used for stats
    """

    def __init__(self, id_creator: Callable):
        self.id_creator = id_creator

    def create_events(self, game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player],
                      data_frame, kickoff_frames, first_touch_frames):
        self.calculate_hit_stats(game, proto_game, player_map, data_frame, kickoff_frames, first_touch_frames)
        self.calculate_ball_carries()

    def calculate_hit_stats(self, game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player],
                            data_frame, kickoff_frames, first_touch_frames):
        logger.info("Looking for hits.")
        hits = BaseHit.get_hits_from_game(game, proto_game, self.id_creator, data_frame, first_touch_frames)
        logger.info("Found %s hits." % len(hits))

        SaltieHit.get_saltie_hits_from_game(proto_game, hits, player_map, data_frame, kickoff_frames)
        logger.info("Analysed hits.")

        # self.stats = get_stats(self)
