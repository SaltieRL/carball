import pandas as pd
import math
from typing import List

from carball.generated.api.stats.events_pb2 import Hit
from carball.generated.api import game_pb2
from carball.json_parser.game import Game

class PressureAnalysis:
    def __init__(self, game: Game, proto_game: game_pb2, data_frame: pd.DataFrame):
        """Initialize a new instance of pressure analysis."""
        self.proto_game = proto_game
        self.game = game
        self.data_frame = data_frame

    def get_distance(self, position1: List[float], position2: List[float]) -> float:
        """Perform distance formula in any dimension between two positions."""
        if len(position1) != len(position2):
            return -1

        squared_distances = 0
        for dimension in range(len(position1)):
            squared_distances += (position1[dimension] - position2[dimension])**2
        return math.sqrt(squared_distances)

    def get_hit_pressure(self, hit: Hit):
        """Calculate pressure for the passed hit. Hit pressure determines how long it would have taken for the nearest opponent to hit the ball."""
        highest_pressure = 0
        teams = self.proto_game.teams
        opposing_team = None
        try:
            opposing_team = next(filter(lambda x: hit.player_id not in x.player_ids, teams))
        except StopIteration:
            hit.pressure = 0
            return
        opposing_team_ids = list(map(lambda x: x.id, opposing_team.player_ids))
        for player_id in opposing_team_ids:
            ball_row = self.data_frame.ball.iloc[hit.frame_number]
            player_name = None
            try:
                player_name = next(filter(lambda x: x.id.id == player_id, self.proto_game.players)).name
            except StopIteration:
                hit.pressure = 0
                break
            player_row = self.data_frame[player_name].iloc[hit.frame_number]

            # Get kinematics. Divide by 30 to consider velocity as uu/frame.
            ball_position = [ball_row.pos_x,ball_row.pos_y,ball_row.pos_z]
            player_position = [player_row.pos_x,player_row.pos_y,player_row.pos_z]
            player_velocity = [player_row.vel_x/30,player_row.vel_y/30,player_row.vel_z/30]

            original_distance = self.get_distance(ball_position, player_position)
            # Only consider defenders within 2000uu of hit.
            if original_distance < 2000:
                # Check the next 10 frames to see if the opposing player would have hit the ball.
                for i in range(100):
                    frame = i/10
                    estimated_player_position = [player_position[x]+frame*player_velocity[x] for x in range(len(ball_position))]
                    new_distance = self.get_distance(estimated_player_position,ball_position)
                    if new_distance > original_distance and new_distance > 500:
                        # Defender is not going towards ball, stop checking
                        break
                    if new_distance < 500:
                        highest_pressure = int(max(highest_pressure, (10-frame)*10))
                        break
        hit.pressure = highest_pressure

    def calculate_pressure_stats(self):
        """Will assign a pressure value to every hit in the game."""
        for hit in self.proto_game.game_stats.hits:
            self.get_hit_pressure(hit)
