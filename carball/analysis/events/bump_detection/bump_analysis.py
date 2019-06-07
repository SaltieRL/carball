from typing import Callable, Dict

import pandas as pd
from carball.generated.api.stats.events_pb2 import Bump

from carball.generated.api.player_id_pb2 import PlayerId
from carball.generated.api.player_pb2 import Player
from carball.json_parser.game import Game

from carball.generated.api import game_pb2


class BumpAnalysis:
    def __init__(self, game: Game, proto_game: game_pb2):
        self.proto_game = proto_game

    def get_bumps_from_game(self, game: Game, proto_game: game_pb2, id_creation: Callable,
                               player_map: Dict[str, Player],
                               data_frame: pd.DataFrame, kickoff_frames: pd.DataFrame):
        self.create_bumps_from_demos(proto_game)

        self.analyze_bumps(kickoff_frames)

    def create_bumps_from_demos(self, proto_game):
        for index in range(len(proto_game.metadata.demos)):
            demo = proto_game.metadata.demos[0]
            self.add_bump(demo.frame_number, demo.vicim_id, demo.attacker_id, True)

    def add_bump(self, frame: int, victim_id: PlayerId, attacker_id: PlayerId, is_demo: bool) -> Bump:
        bump = self.proto_game.game_stats.bumps.add()
        bump.frame_number = frame
        bump.attacker_id = attacker_id
        bump.victim_id = victim_id
        if is_demo:
            bump.is_demo = True
