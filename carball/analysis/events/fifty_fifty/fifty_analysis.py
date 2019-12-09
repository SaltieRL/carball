import pandas as pd
import math
from typing import List

from carball.generated.api.stats.events_pb2 import FiftyFifty
from carball.generated.api import game_pb2
from carball.json_parser.game import Game

class FiftyAnalysis:
    def __init__(self, game: Game, proto_game: game_pb2, data_frame: pd.DataFrame):
        """Initialize a new instance of 50/50 analysis."""
        self.proto_game = proto_game
        self.game = game
        self.data_frame = data_frame
        self.fifty_threshold = 5

    def determine_fifty_fifty_winner(self, fifty, next_hit_index):
        """Iterate all 50/50s and determine the winner of each."""
        hits = self.proto_game.game_stats.hits
        hit = hits[next_hit_index]
        following_hit = hits[next_hit_index+1]
        last_hit_of_fifty = fifty.hits[-1]

        # If the last hit was a very useful hit, then it was won by the hitter.
        if last_hit_of_fifty.goal or last_hit_of_fifty.save or last_hit_of_fifty.clear or last_hit_of_fifty.assist or last_hit_of_fifty.pass_:
            fifty.winner = last_hit_of_fifty.player_id
            return

        # If the next hit starts a 50/50, then this hit was a neutral 50/50.
        if (following_hit.frame_number - hit.frame_number) < self.fifty_threshold:
            fifty.is_neutral = True
        else:
            # Winner is whichever team successfully recovered the ball.
            fifty.winner = hit.player_id

    def calculate_fifty_fifty_stats(self):
        """Find all 50/50s in a match and assign their winners."""
        hits = self.proto_game.game_stats.hits
        # Check all hits for 50.50 potential.
        i = 0
        while i < range(len(hits)-1):
            hit = hits[i]
            lookahead = hits[i+1]
            hits_in_fifty = []
            players_involved = set()
            # If two hits are within threshold, we are starting a 50/50.
            if (lookahead.frame_number - hit.frame_number) < self.fifty_threshold:
                hits_in_fifty.append(hit)
                hits_in_fifty.append(lookahead)
                players_involved.add(hit.player_id)
                players_involved.add(lookahead.player_id)
            i += 1
            # Break if that was the last hit.
            if i >= len(hits):
                break
            hit = hits[i]
            lookahead = hits[i+1]
            while (lookahead.frame_number - hit.frame_number) < self.fifty_threshold:
                hits_in_fifty.append(lookahead)
                players_involved.add(lookahead.player_id)
                i += 1
                # Break if that was the last hit.
                if i >= len(hits):
                    break
                hit = hits[i]
                lookahead = hits[i+1]
            # Check if a 50/50 was found.
            if len(hits_in_fifty) >= 1:
                fifty = self.proto_game.game_stats.fifty_fifties.add()
                fifty.hits = hits_in_fifty
                fifty.players = list(players_involved)
                fifty.starting_frame = hits_in_fifty[0].frame_number
                fifty.ending_frame = hits_in_fifty[-1].frame_number
                self.determine_fifty_fifty_winner(fifty, i+1)
