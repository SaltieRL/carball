from typing import TYPE_CHECKING, Dict

from .averages import Averages
from .positional_tendencies import PositionalTendencies as PT

if TYPE_CHECKING:
    from analysis.saltie_game.saltie_game import SaltieGame


class TendenciesStat:
    def __init__(self,
                 positional_tendencies: Dict[str, PT],
                 averages: Dict[str, Averages]
                 ):
        self.positional_tendencies = positional_tendencies
        self.averages = averages

    @classmethod
    def get_tendencies(cls, game: 'SaltieGame') -> 'TendenciesStat':
        positional_tendencies: Dict[str, PT] = {
            player.name: PT.get_player_tendencies(player, game)
            for team in game.api_game.teams for player in team.players
        }

        averages: Dict[str, Averages] = {
            player.name: Averages.get_averages_for_player(player, game)
            for team in game.api_game.teams for player in team.players
        }
        return cls(positional_tendencies=positional_tendencies, averages=averages)
