from typing import TYPE_CHECKING

from .player_tendencies import PlayerTendencies as PT

if TYPE_CHECKING:
    from analysis.saltie_game.saltie_game import SaltieGame


class TendenciesStat:
    def __init__(self, player_tendencies):
        self.player_tendencies = player_tendencies
        import pprint
        pprint.pprint(player_tendencies)

    @classmethod
    def get_tendencies(cls, game: 'SaltieGame') -> 'TendenciesStat':
        player_tendencies = {
            player.name: PT.get_player_tendencies(player, game)
            for team in game.api_game.teams for player in team.players
        }
        return cls(player_tendencies)
