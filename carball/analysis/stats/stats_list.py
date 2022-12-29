from typing import List

from carball.analysis.stats.demos.demos import DemoStat
from carball.analysis.stats.dribbles.ball_carry import CarryStat
from carball.analysis.stats.kickoffs.kickoff_stat import KickoffStat
from carball.analysis.stats.possession.per_possession import PerPossessionStat
from carball.analysis.stats.ball_forward.distance_hit_ball_forward import DistanceStats
from carball.analysis.stats.boost.boost import BoostStat
from carball.analysis.stats.controls.controls import ControlsStat
from carball.analysis.stats.possession.ball_distances import BallDistanceStat
from carball.analysis.stats.possession.possession import PossessionStat
from carball.analysis.stats.possession.turnovers import TurnoverStat
from carball.analysis.stats.stats import BaseStat, HitStat
from carball.analysis.stats.tendencies.averages import Averages
from carball.analysis.stats.tendencies.hit_counts import HitCountStat
from carball.analysis.stats.tendencies.positional_tendencies import PositionalTendencies
from carball.analysis.stats.tendencies.relative_position_tendencies import RelativeTendencies
from carball.analysis.stats.tendencies.speed_tendencies import SpeedTendencies
from carball.analysis.stats.tendencies.team_tendencies import TeamTendencies
from carball.analysis.stats.rumble.rumble import RumbleItemStat
from carball.analysis.stats.rumble.goals import PreRumbleGoals, ItemGoals
from carball.analysis.stats.dropshot.goals import DropshotGoals
from carball.analysis.stats.dropshot.ball_phase_times import DropshotBallPhaseTimes
from carball.analysis.stats.dropshot.damage import DropshotStats


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
                SpeedTendencies(),
                CarryStat(),
                PerPossessionStat(),
                SpeedTendencies(),
                RumbleItemStat(),
                KickoffStat(),
                DropshotStats(),
                DemoStat()
                ]

    @staticmethod
    def get_team_stats() -> List[BaseStat]:
        """These are stats that end up being assigned to a specific team"""
        return [PossessionStat(),
                TeamTendencies(),
                RelativeTendencies(),
                PerPossessionStat(),
                RumbleItemStat(),
                PreRumbleGoals(),
                DropshotStats()
                ]

    @staticmethod
    def get_general_stats() ->List[BaseStat]:
        """These are stats that end up being assigned to the game as a whole"""
        return [PositionalTendencies(),
                SpeedTendencies(),
                ItemGoals(),
                DropshotGoals(),
                DropshotBallPhaseTimes(),
                DropshotStats()
                ]

    @staticmethod
    def get_hit_stats() ->List[HitStat]:
        """These are stats that depend on current hit and next hit"""
        return [DistanceStats(),
                PossessionStat(),
                HitCountStat(),
                TurnoverStat()
                ]
