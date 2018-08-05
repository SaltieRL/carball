import pandas as pd

from json_parser.base_game.game import Game
from json_parser.base_game.player import Player


class PlayerTendencies:

    def __init__(self,
                 height_0: float = None, height_1: float = None, height_2: float = None,
                 half_0: float = None, half_1: float = None,
                 third_0: float = None, third_1: float = None, third_2: float = None,
                 ball_0: float = None, ball_1: float = None,
                 ):
        """

        :param height_0: Time spent on ground
        :param height_1: Time spent low in air
        :param height_2: Time spent high in air
        :param half_0: Time spent in defending half
        :param half_1: Time spent in attacking half
        :param third_0: Time spent in defending third
        :param third_1: Time spent in middle third
        :param third_2: Time spent in attacking third
        :param ball_0: Time spent behind ball
        :param ball_1: Time spent ahead of ball
        """
        pass

    @staticmethod
    def get_player_tendencies(player: Player, game: Game):
        data_frame_deltas = pd.concat(
            [
                player.data,
                game.frames.delta
            ],
            axis=1
        )
        pass
