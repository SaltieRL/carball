from .possession import PossessionStat
from game.game import Game


def add_stats(game: Game):
    game.stats = {
        'posession': PossessionStat.get_possession(game)
    }
