from typing import Dict

from json_parser.game import Game
from json_parser.player import Player
from .player_tendencies import PlayerTendencies


class TendenciesStat:
    def __init__(self, player_tendencies: Dict[Player, PlayerTendencies]):
        self.player_tendencies = player_tendencies

    @classmethod
    def get_tendencies(cls, game: Game) -> 'TendenciesStat':
        player_tendencies = {
            player: PlayerTendencies.get_player_tendencies(game.goal_data_frame[player.name], game) for player in game.players
        }
        return cls(player_tendencies)

