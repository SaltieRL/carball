from typing import List

from replay_analysis.analysis.stats.ball_forward.distance_hit_ball_forward import DistanceStats
from replay_analysis.analysis.stats.boost.boost import BoostStat
from replay_analysis.analysis.stats.possession.possession import PossessionStat
from replay_analysis.analysis.stats.possession.turnovers import TurnoverStat
from replay_analysis.analysis.stats.stats import BaseStat, HitStat
from replay_analysis.analysis.stats.tendencies.tendencies import TendenciesStat


class StatsList:
    """
    Where you add any extra stats you want calculated
    """
    @staticmethod
    def get_player_stats() -> List[BaseStat]:
        """These are stats that end up being assigned to a specific player"""
        return [BoostStat(),
                TendenciesStat()
                ]

    @staticmethod
    def get_team_stats() -> List[BaseStat]:
        """These are stats that end up being assigned to a specific team"""
        return [PossessionStat()]

    @staticmethod
    def get_general_stats() ->List[BaseStat]:
        """These are stats that end up being assigned to the game as a whole"""
        return [TurnoverStat()]

    @staticmethod
    def get_hit_stats() ->List[HitStat]:
        """These are stats that depend on current hit and next hit"""
        return [DistanceStats(),
                PossessionStat()
                ]
