from typing import List

from ...analysis.stats.tendencies.speed_tendencies import SpeedTendencies
from ...analysis.stats.tendencies.averages import Averages
from ...analysis.stats.possession.ball_distances import BallDistanceStat
from ...analysis.stats.tendencies.hit_counts import HitCountStat
from ...analysis.stats.ball_forward.distance_hit_ball_forward import DistanceStats
from ...analysis.stats.boost.boost import BoostStat
from ...analysis.stats.possession.possession import PossessionStat
from ...analysis.stats.possession.turnovers import TurnoverStat
from ...analysis.stats.stats import BaseStat, HitStat
from ...analysis.stats.tendencies.positional_tendencies import PositionalTendencies
from ...analysis.stats.controls.controls import ControlsStat


class StatsList:
    """
    Where you add any extra stats you want calculated.
    """

    @staticmethod
    def get_player_stats() -> List[BaseStat]:
        """These are stats that end up being assigned to a specific player"""
        return [BoostStat(),
                PositionalTendencies(),
                Averages(),
                BallDistanceStat(),
                ControlsStat(),
                SpeedTendencies()
                ]

    @staticmethod
    def get_team_stats() -> List[BaseStat]:
        """These are stats that end up being assigned to a specific team"""
        return [PossessionStat()]

    @staticmethod
    def get_general_stats() ->List[BaseStat]:
        """These are stats that end up being assigned to the game as a whole"""
        return []

    @staticmethod
    def get_hit_stats() ->List[HitStat]:
        """These are stats that depend on current hit and next hit"""
        return [DistanceStats(),
                PossessionStat(),
                HitCountStat(),
                TurnoverStat()
                ]
