import pandas as pd
import math
from typing import List

from carball.generated.api.stats.events_pb2 import FiftyFifty
from carball.generated.api.stats.events_pb2 import Hit
from carball.generated.api import game_pb2
from carball.json_parser.game import Game

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
        last_hit_of_fifty = fifty.hits[-1]

        # If the last hit was a very useful hit, then it was won by the hitter.
        if last_hit_of_fifty.goal or last_hit_of_fifty.save or last_hit_of_fifty.clear or last_hit_of_fifty.assist or last_hit_of_fifty.pass_:
            fifty.winner.CopyFrom(last_hit_of_fifty.player_id)
            return

        # If the next hit starts a 50/50, then this hit was a neutral 50/50.
        if self.hits_are_consecutive(hit,following_hit):
            fifty.is_neutral = True
        else:
            # Winner is whichever team successfully recovered the ball.
            fifty.winner.CopyFrom(hit.player_id)

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
                hits_in_fifty.append(hit)
                hits_in_fifty.append(lookahead)
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
                hits_in_fifty.append(lookahead)
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
                fifty.starting_frame = hits_in_fifty[0].frame_number
                fifty.ending_frame = hits_in_fifty[-1].frame_number
                self.determine_fifty_fifty_winner(fifty, i+1)
