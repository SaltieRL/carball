from typing import Dict, TYPE_CHECKING

from .boost.boost import BoostStat
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
        'boost': BoostStat.get_boost(saltie_game)
    }



