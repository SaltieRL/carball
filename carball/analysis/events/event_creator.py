import logging
from typing import Dict, Callable

import pandas as pd

from carball.analysis.events.bump_detection.bump_analysis import BumpAnalysis
from carball.analysis.events.boost_pad_detection.pickup_analysis import PickupAnalysis
from carball.analysis.events.hit_pressure.pressure_analysis import PressureAnalysis
from carball.analysis.events.fifty_fifty.fifty_analysis import FiftyAnalysis
from carball.analysis.events.kickoff_detection.kickoff_analysis import BaseKickoff
from carball.analysis.events.carry_detection import CarryDetection
from carball.analysis.events.hit_detection.base_hit import BaseHit
from carball.analysis.events.hit_detection.hit_analysis import SaltieHit
from carball.analysis.events.dropshot.damage import create_dropshot_damage_events
from carball.analysis.events.dropshot.ball import create_dropshot_ball_events
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
                      data_frame: pd.DataFrame, kickoff_frames: pd.DataFrame, first_touch_frames: pd.Series,
                      calculate_intensive_events: bool = False):
        """
        Creates all of the event protos.
        :param calculate_intensive_events: Indicates if expensive calculations should run to include additional stats.
        """
        goal_frames = data_frame.game.goal_number.notnull()
        self.create_boostpad_events(proto_game, data_frame)
        self.create_hit_events(game, proto_game, player_map, data_frame, kickoff_frames, first_touch_frames)
        self.calculate_kickoff_stats(game, proto_game, player_map, data_frame, kickoff_frames, first_touch_frames)
        self.calculate_ball_carries(game, proto_game, player_map, data_frame[goal_frames])
        self.create_bumps(game, proto_game, player_map, data_frame[goal_frames])
        self.create_dropshot_events(game, proto_game, player_map)

        if calculate_intensive_events:
            self.calculate_hit_pressure(game, proto_game, data_frame)
            self.calculate_fifty_fifty(game, proto_game, data_frame)
            # TODO (j-wass): calculate bumps

    def calculate_fifty_fifty(self, game: Game, proto_game: game_pb2.Game, data_frame: pd.DataFrame):
        logger.info("Calculating 50/50s.")
        fiftyAnalysis = FiftyAnalysis(game=game, proto_game=proto_game, data_frame=data_frame)
        fiftyAnalysis.calculate_fifty_fifty_stats()

    def calculate_hit_pressure(self, game: Game, proto_game: game_pb2.Game, data_frame: pd.DataFrame):
        logger.info("Calculating hit pressure.")
        pressureAnalysis = PressureAnalysis(game=game, proto_game=proto_game, data_frame=data_frame)
        pressureAnalysis.calculate_pressure_stats()

    def calculate_kickoff_stats(self, game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player],
                                data_frame, kickoff_frames, first_touch_frames):
        logger.info("Looking for kickoffs.")
        kickoffs = BaseKickoff.get_kickoffs_from_game(game, proto_game, self.id_creator, player_map, data_frame, kickoff_frames, first_touch_frames)
        logger.info("Found %s kickoffs." % len(kickoffs.keys()))

    def create_hit_events(self, game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player],
                          data_frame: pd.DataFrame, kickoff_frames: pd.DataFrame, first_touch_frames: pd.Series):
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
                               data_frame: pd.DataFrame):
        logger.info("Looking for carries.")
        carry_detection = CarryDetection()
        carry_data = carry_detection.filter_frames(data_frame)

        for player in player_map:
            carry_detection.create_carry_events(carry_data, player_map[player], proto_game, data_frame)
            # find now continuous data of longer than a second.
        logger.info("Found %s carries.", len(proto_game.game_stats.ball_carries))

    def create_bumps(self, game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player],
                     data_frame: pd.DataFrame):
        logger.info("Looking for bumps.")
        bumpAnalysis = BumpAnalysis(game=game, proto_game=proto_game)
        bumpAnalysis.get_bumps_from_game(data_frame)
        logger.info("Found %s bumps.", len(proto_game.game_stats.bumps))

    def create_dropshot_events(self, game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player]):
        create_dropshot_damage_events(game, proto_game)
        create_dropshot_ball_events(game, proto_game, player_map)

    def create_boostpad_events(self, proto_game: game_pb2.Game, data_frame: pd.DataFrame):
        PickupAnalysis.add_pickups(proto_game, data_frame)
