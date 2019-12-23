import pandas as pd
import numpy as np

from carball.generated.api.stats.events_pb2 import FiftyFifty
from carball.generated.api.stats.events_pb2 import Hit
from carball.generated.api import game_pb2
from carball.json_parser.game import Game
from carball.analysis.constants.field_constants import HEIGHT_1_LIM, STANDARD_FIELD_LENGTH_HALF, MAX_CAR_SPEED

class FiftyAnalysis:
    def __init__(self, game: Game, proto_game: game_pb2, data_frame: pd.DataFrame):
        """Initialize a new instance of 50/50 analysis."""
        self.proto_game = proto_game
        self.game = game
        self.data_frame = data_frame
        self.fifty_threshold = 5

    def hits_are_consecutive(self, hit1: Hit, hit2: Hit):
        """Return True if hit2 occurs right after hit1 and are from different players."""
        withinThreshold = (hit2.frame_number - hit1.frame_number) < self.fifty_threshold
        opposingPlayers = hit1.player_id.id != hit2.player_id.id
        return withinThreshold and opposingPlayers

    def determine_fifty_fifty_winner(self, fifty: FiftyFifty, next_hit_index: int):
        """Iterate all 50/50s and determine the winner of each."""
        hits = self.proto_game.game_stats.hits
        hit = hits[next_hit_index]
        following_hit = hits[next_hit_index+1]
        last_hit_of_fifty = hits[next_hit_index-1]

        # If the last hit was a very useful hit, then it was won by the hitter.
        if last_hit_of_fifty.goal or last_hit_of_fifty.save or last_hit_of_fifty.clear or last_hit_of_fifty.assist or last_hit_of_fifty.pass_:
            fifty.winner.CopyFrom(last_hit_of_fifty.player_id)
            return

        # If the next hit starts a 50/50, then this hit was a neutral 50/50.
        if self.hits_are_consecutive(hit,following_hit):
            fifty.is_neutral = True
            return

        # Check for dunks.
        # If the first hit of the fifty is a kickoff, don't care about dunks.
        if hits[fifty.hits[0]].is_kickoff:
            fifty.is_neutral = True
            return

        last_hit_frame = last_hit_of_fifty.frame_number

        goal_pos_orange = [0, STANDARD_FIELD_LENGTH_HALF, HEIGHT_1_LIM/2]
        goal_pos_blue = [0, -1*STANDARD_FIELD_LENGTH_HALF, HEIGHT_1_LIM/2]

        # Get the ball position at the time of the hit.
        # Consider the vector from this position to each goal.
        ball_row = self.data_frame.ball.iloc[last_hit_frame+self.fifty_threshold]
        pos_vector_to_blue = [goal_pos_blue[0] - ball_row.pos_x, goal_pos_blue[1] - ball_row.pos_y, goal_pos_blue[2] - ball_row.pos_z]
        pos_vector_to_orange = [goal_pos_orange[0] - ball_row.pos_x, goal_pos_orange[1] - ball_row.pos_y, goal_pos_orange[2] - ball_row.pos_z]

        # Test the ball velocity slightly in the future so that it experiences no more acceleration from any hit.
        ball_row = self.data_frame.ball.iloc[last_hit_frame+self.fifty_threshold]
        ball_velocity = [ball_row.vel_x,ball_row.vel_y,ball_row.vel_z]

        # Find the component of velocity projected onto the vectors towards each goal.
        # If either dot product is significant, then the ball was speeding towards that goal.
        projection_to_blue_goal = np.dot(np.array(ball_velocity), np.array(pos_vector_to_blue))/np.linalg.norm(np.array(pos_vector_to_blue))
        projection_to_orange_goal = np.dot(np.array(ball_velocity), np.array(pos_vector_to_orange))/np.linalg.norm(np.array(pos_vector_to_orange))
        towards_blue_net = projection_to_blue_goal > MAX_CAR_SPEED and projection_to_orange_goal < -1*MAX_CAR_SPEED
        towards_orange_net = projection_to_orange_goal > MAX_CAR_SPEED and projection_to_blue_goal < -1*MAX_CAR_SPEED

        # If the last hit travelled for a while.
        last_hit_travel_time = hit.frame_number - last_hit_of_fifty.frame_number
        if last_hit_travel_time > self.fifty_threshold * 5:
            # Check if the ball was moving towards either net
            if towards_blue_net:
                # Find the last orange player to hit the ball towards the blue net. They are the winner.
                for i in range(len(fifty.hits)):
                    fifty_hit_index = fifty.hits[-1*i-1]
                    fifty_hit = hits[fifty_hit_index]
                    fifty_hit_player_id = fifty_hit.player_id
                    fifty_hit_player = next(filter(lambda x: x.id == fifty_hit_player_id,self.proto_game.players))
                    if fifty_hit_player and fifty_hit_player.is_orange:
                        fifty_hit.dunk = True
                        fifty.winner.CopyFrom(fifty_hit.player_id)
                        return
            if towards_orange_net:
                # Find the last blue player to hit the ball towards the orange net. They are the winner.
                for i in range(len(fifty.hits)):
                    fifty_hit_index = fifty.hits[-1*i-1]
                    fifty_hit=hits[fifty_hit_index]
                    fifty_hit_player_id = fifty_hit.player_id
                    fifty_hit_player = next(filter(lambda x: x.id == fifty_hit_player_id,self.proto_game.players))
                    if fifty_hit_player and not fifty_hit_player.is_orange:
                        fifty_hit.dunk = True
                        fifty.winner.CopyFrom(fifty_hit.player_id)
                        return

        # Nothing special happened after 50/50.
        fifty.is_neutral = True

    def calculate_fifty_fifty_stats(self):
        """Find all 50/50s in a match and assign their winners."""
        hits = self.proto_game.game_stats.hits
        # Check all hits for 50/50 potential.
        i = 0
        while i < len(hits)-1:
            hit = hits[i]
            lookahead = hits[i+1]
            hits_in_fifty = []
            players_involved = {}
            # If two hits are within threshold, we are starting a 50/50.
            if not self.hits_are_consecutive(hit,lookahead):
                # If no 50/50 found, go to next hit.
                i += 1
                continue
            else:
                # 50/50 detected.
                hits_in_fifty.append(i)
                hits_in_fifty.append(i+1)
                players_involved[hit.player_id.id] = hit.player_id
                players_involved[lookahead.player_id.id] = lookahead.player_id
            # Check next hit, break if that was the last hit.
            i += 1
            if i >= len(hits)-1:
                break
            hit = hits[i]
            lookahead = hits[i+1]
            # Start iterating hits that are all in 50/50.
            while self.hits_are_consecutive(hit, lookahead):
                hits_in_fifty.append(i+1)
                players_involved[lookahead.player_id.id] = lookahead.player_id
                # Break if that was the last hit.
                i += 1
                if i >= len(hits)-1:
                    break
                hit = hits[i]
                lookahead = hits[i+1]
            # Build 50/50 object.
            if len(hits_in_fifty) >= 1:
                fifty = self.proto_game.game_stats.fifty_fifties.add()
                fifty.hits.extend(hits_in_fifty)
                fifty.players.extend(list(players_involved.values()))
                fifty.starting_frame = hits[hits_in_fifty[0]].frame_number
                fifty.ending_frame = hits[hits_in_fifty[-1]].frame_number
                self.determine_fifty_fifty_winner(fifty, i+1)
