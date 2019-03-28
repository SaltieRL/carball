import logging
from typing import Dict, Callable

from carball.analysis.events.hit_detection.base_hit import BaseHit
from carball.analysis.events.hit_detection.hit_analysis import SaltieHit
from carball.generated.api import game_pb2
from carball.generated.api.player_pb2 import Player
from carball.json_parser.game import Game

logger = logging.getLogger(__name__)


class EventsCreator:
    """
        Handles the creation of all events that can then be later used for stats
    """

    def __init__(self, id_creator: Callable):
        self.id_creator = id_creator

    def create_events(self, game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player],
                      data_frame, kickoff_frames, first_touch_frames):
        """
        Creates all of the event protos.
        """
        self.create_hit_events(game, proto_game, player_map, data_frame, kickoff_frames, first_touch_frames)
        # self.calculate_ball_carries()

    def create_hit_events(self, game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player],
                          data_frame, kickoff_frames, first_touch_frames):
        """
        Creates all of the events for hits
        """
        logger.info("Looking for hits.")
        hits = BaseHit.get_hits_from_game(game, proto_game, self.id_creator, data_frame, first_touch_frames)
        logger.info("Found %s hits." % len(hits))

        SaltieHit.get_saltie_hits_from_game(proto_game, hits, player_map, data_frame, kickoff_frames)
        logger.info("Analysed hits.")

        # self.stats = get_stats(self)

    def calculate_ball_carries(self, game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player],
                               data_frame, kickoff_frames, first_touch_frames):
        pass
