from typing import Dict, TYPE_CHECKING

from .positioning.positioning import PositioningStat
from .possession.possession import PossessionStat
from .possession.turnovers import TurnoverStat
from .tendencies.tendencies import TendenciesStat

if TYPE_CHECKING:
    from ..saltie_game.saltie_game import SaltieGame


def get_stats(saltie_game: 'SaltieGame') -> Dict:
    return {
        'tendencies': TendenciesStat.get_tendencies(saltie_game),
        'possession': PossessionStat.get_possession(saltie_game),
        'turnovers': TurnoverStat.get_player_turnovers(saltie_game),
        'time_in_half': PositioningStat.get_player_half_percentages(saltie_game),
        'average_speed': PositioningStat.get_player_speeds(saltie_game),
    }



