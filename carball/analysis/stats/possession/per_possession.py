from collections import Counter, defaultdict
from typing import List, Dict, Tuple

import pandas as pd

from carball.generated.api.stats.team_stats_pb2 import TeamStats
from ....analysis.stats.stats import BaseStat
from ....generated.api import game_pb2
from ....generated.api.player_pb2 import Player
from ....generated.api.stats.events_pb2 import Hit
from ....generated.api.stats.per_possession_stats_pb2 import PerPossessionStats
from ....generated.api.stats.player_stats_pb2 import PlayerStats
from ....json_parser.game import Game


class PerPossessionStat(BaseStat):
    possession_hit_fields = [
        'pass_', 'passed',
        'dribble', 'dribble_continuation',
        'shot', 'goal',
        'assist', 'assisted',
        'save',
        'aerial',
    ]

    def __init__(self):
        super().__init__()
        self.initialized = False

        self.player_possessions = []
        self.team_possessions = []

        self.player_possessions_dict = {}
        self.team_possessions_dict = {}

    def initialize(self, proto_game: game_pb2.Game, player_map: Dict[str, Player],
                   data_frame: pd.DataFrame):
        _player_possessions, _team_possessions = self.get_possessions(proto_game, player_map)

        for possessions in (_player_possessions, _team_possessions):
            self.add_possession_durations(possessions, data_frame)

        # Remove possessions that are 1-hit or <1s
        self.player_possessions = [
            player_possession for player_possession in _player_possessions
            if len(player_possession.hits) > 1 and player_possession.duration > 1
        ]
        self.team_possessions = [
            team_possession for team_possession in _team_possessions
            if len(team_possession.hits) > 1 and team_possession.duration > 1
        ]
        self.logger.debug(f"Found {len(self.player_possessions)} player possessions and "
                         f"{len(self.team_possessions)} team possessions.")

        for possessions in (self.player_possessions, self.team_possessions):
            self.add_possession_counts(possessions)
            self.add_possession_distances(possessions)

        # Sort player_possessions by player
        self.player_possessions_dict = defaultdict(list)
        for possession in self.player_possessions:
            self.player_possessions_dict[possession.player_id].append(possession)

        # Sort team_possessions by team
        self.team_possessions_dict: Dict[bool, List['TeamPossession']] = defaultdict(list)
        for possession in self.team_possessions:
            self.team_possessions_dict[possession.is_orange].append(possession)

        self.initialized = True

    def calculate_player_stat(self, player_stat_map: Dict[str, PlayerStats], game: Game, proto_game: game_pb2.Game,
                              player_map: Dict[str, Player], data_frame: pd.DataFrame):
        if not self.initialized:
            self.initialize(proto_game, player_map, data_frame)

        player_possession_stats_dict: Dict[str, List['PlayerPossession']] = {}
        for player_id, possessions in self.player_possessions_dict.items():
            stats = self.get_per_possession_stats(possessions)

            player_stat_map[player_id].per_possession_stats.CopyFrom(stats)

            player_possession_stats_dict[player_id] = stats

        for player_id, player_stats in player_stat_map.items():
            if player_id in player_possession_stats_dict:
                player_stats.per_possession_stats.CopyFrom(player_possession_stats_dict[player_id])

    def calculate_team_stat(self, team_stat_list: Dict[int, TeamStats], game: Game, proto_game: game_pb2.Game,
                            player_map: Dict[str, Player], data_frame: pd.DataFrame):
        for team_is_orange, possessions in self.team_possessions_dict.items():
            stats = self.get_per_possession_stats(possessions)
            team_stat_list[team_is_orange].per_possession_stats.CopyFrom(stats)

    @staticmethod
    def get_possessions(proto_game: game_pb2.Game,
                        player_map: Dict[str, Player]) -> Tuple[List['PlayerPossession'], List['TeamPossession']]:
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

        return player_possessions, team_possessions

    @staticmethod
    def add_possession_durations(possessions: List['BasePossession'], data_frame: pd.DataFrame):
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

            try:
                possession_times = data_frame.loc[[possession_start_frame, possession_end_frame], ('game', 'time')].values
                possession_duration = possession_times[1] - possession_times[0]
            except KeyError:
                possession_duration = 0
            possession.duration = possession_duration

    @classmethod
    def add_possession_counts(cls, possessions: List['BasePossession']):
        for possession in possessions:
            for hit in possession.hits:
                for field in cls.possession_hit_fields:
                    if getattr(hit, field):
                        possession.counts[field] += 1

    @staticmethod
    def add_possession_distances(possessions: List['BasePossession']):
        for possession in possessions:
            distance = 0
            for hit in possession.hits:
                distance += hit.distance
            possession.distance = distance

    @classmethod
    def get_per_possession_stats(cls, possessions: List['BasePossession']) -> PerPossessionStats:
        count = len(possessions)
        hit_counts = [len(possession.hits) for possession in possessions]
        average_hits = sum(hit_counts) / len(hit_counts)
        durations = [possession.duration for possession in possessions]
        average_duration = sum(durations) / len(durations)

        average_counts = {}

        for field in cls.possession_hit_fields:
            sum_ = sum([possession.counts[field] for possession in possessions])
            average_counts[field] = sum_ / count

        per_possession_stats = PerPossessionStats()
        cls.add_average_counts(per_possession_stats, average_counts)

        per_possession_stats.average_hits = average_hits
        per_possession_stats.average_duration = average_duration
        per_possession_stats.count = count

        return per_possession_stats

    @staticmethod
    def add_average_counts(per_possession_stats: PerPossessionStats, average_counts: Dict[str, float]):
        for field, value in average_counts.items():
            setattr(per_possession_stats.average_counts, field, value)


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
