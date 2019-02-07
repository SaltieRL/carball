from collections import Counter
from typing import List, Dict, Tuple

import pandas as pd

from carball.analysis.stats.possession_based_stats import PerPossessionStats
from carball.generated.api.stats.events_pb2 import Hit
from ...generated.api import game_pb2
from ...generated.api.player_pb2 import Player
from ...json_parser.game import Game


def analyse_possessions(game: Game, proto_game: game_pb2.Game,
                        player_map: Dict[str, Player], data_frame: pd.DataFrame):
    player_possessions, team_possessions = get_possessions(game, proto_game, player_map, data_frame)

    for possessions in (player_possessions, team_possessions):
        add_possession_durations(possessions, game, proto_game, player_map, data_frame)
        add_possession_counts(possessions)
        add_possession_distances(possessions)

    # Sort player_possessions by player
    player_possessions_dict = {}
    for possession in player_possessions:
        player_id = possession.player_id
        if player_id not in player_possessions_dict:
            player_possessions_dict[player_id] = []
        player_possessions_dict[player_id].append(possession)

    player_possession_stats_dict = {}
    for player_id, possessions in player_possessions_dict.items():
        stats = PerPossessionStats(possessions)
        player_possession_stats_dict[player_id] = stats

    # Sort team_possessions by team
    team_possessions_dict = {}
    for possession in team_possessions:
        team_is_orange = possession.is_orange
        if team_is_orange not in team_possessions_dict:
            team_possessions_dict[team_is_orange] = []
        team_possessions_dict[team_is_orange].append(possession)

    team_possession_stats_dict = {}
    for team_is_orange, possessions in team_possessions_dict.items():
        stats = PerPossessionStats(possessions)
        team_possession_stats_dict[team_is_orange] = stats

    game.player_possessions_dict = player_possessions_dict
    game.player_possession_stats_dict = player_possession_stats_dict
    game.team_possessions_dict = team_possessions_dict
    game.team_possession_stats_dict = team_possession_stats_dict
    pass


def get_possessions(game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player],
                    data_frame: pd.DataFrame) -> Tuple[List['PlayerPossession'], List['TeamPossession']]:
    hits = proto_game.game_stats.hits

    player_possessions: List[PlayerPossession] = []
    team_possessions: List[TeamPossession] = []

    current_goal_number = 0

    current_player_possession = None
    current_team_possession = None

    for hit in hits:
        player_id = hit.player_id.id
        player = player_map[player_id]

        if current_goal_number != hit.goal_number:
            # End current possessions before next goal
            if current_player_possession is not None:
                player_possessions.append(current_player_possession)
                current_player_possession = None
            if current_team_possession is not None:
                team_possessions.append(current_team_possession)
                current_team_possession = None

        current_goal_number = hit.goal_number

        if current_team_possession is None:
            # Start possession
            current_team_possession = TeamPossession([hit], player.is_orange)
        else:
            if current_team_possession.is_orange == player.is_orange:
                # Add to current_team_possession
                current_team_possession.hits.append(hit)
            else:
                # Record last possession and start new
                team_possessions.append(current_team_possession)
                current_team_possession = TeamPossession([hit], player.is_orange)

        if current_player_possession is None:
            # Start possession
            current_player_possession = PlayerPossession([hit], player_id)
        else:
            if current_player_possession.player_id == player_id:
                # Add to current_player_possession
                current_player_possession.hits.append(hit)
            else:
                # Record last possession and start new
                player_possessions.append(current_player_possession)
                current_player_possession = PlayerPossession([hit], player_id)

    print(f"Found {len(player_possessions)} player possessions and {len(team_possessions)} team possessions.")
    return player_possessions, team_possessions


def add_possession_durations(possessions: List['BasePossession'], game: Game, proto_game: game_pb2.Game,
                             player_map: Dict[str, Player], data_frame: pd.DataFrame):
    player_possessions_count = len(possessions)
    for i, possession in enumerate(possessions):
        first_hit = possession.hits[0]
        possession_start_frame = first_hit.frame_number

        if i != player_possessions_count - 1:
            # Next possession exists
            next_possession = possessions[i + 1]
            if next_possession.hits[0].goal_number != first_hit.goal_number:
                # Next possession is in next goal frame
                # possession end frame is end of goal frame
                possession_end_frame = \
                    data_frame.index[(data_frame.loc[:, ('game', 'goal_number')] == first_hit.goal_number)][-1]
            else:
                # possession end frame is first hit of next possession
                possession_end_frame = next_possession.hits[0].frame_number
        else:
            # Last possession of game
            # possession end frame is last frame of game
            possession_end_frame = data_frame.index.max()

        possession_times = data_frame.loc[[possession_start_frame, possession_end_frame], ('game', 'time')].values
        possession_duration = possession_times[1] - possession_times[0]
        possession.duration = possession_duration


def add_possession_counts(possessions: List['BasePossession']):
    fields = [
        'pass_', 'passed',
        'dribble', 'dribble_continuation',
        'shot', 'goal',
        'assist', 'assisted',
        'save',
        'aerial',
    ]
    for possession in possessions:
        for hit in possession.hits:
            for field in fields:
                if getattr(hit, field):
                    possession.counts[field] += 1


def add_possession_distances(possessions: List['BasePossession']):
    for possession in possessions:
        distance = 0
        for hit in possession.hits:
            distance += hit.distance
        possession.distance = distance


class BasePossession:
    def __init__(self, hits: List[Hit]):
        self.hits = hits

        # Added later
        self.duration = None
        self.distance = None
        self.counts = Counter()


class PlayerPossession(BasePossession):
    def __init__(self, hits: List[Hit], player_id: str):
        super().__init__(hits)
        self.player_id = player_id


class TeamPossession(BasePossession):
    def __init__(self, hits: List[Hit], is_orange: bool):
        super().__init__(hits)
        self.is_orange = is_orange
