from typing import TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from ...saltie_game.saltie_game import SaltieGame
    from ...saltie_game.metadata.ApiPlayer import ApiPlayer


class PositioningStat:

    @classmethod
    def get_boost(cls, saltie_game: 'SaltieGame'):
        return cls(PositioningStat.get_player_half_percentages(saltie_game))

    @staticmethod
    def get_player_half_percentages(saltie_game: 'SaltieGame'):
        players = {p.name: [0.0, 0.0] for p in
                   (saltie_game.api_game.teams[0].players + saltie_game.api_game.teams[1].players)}
        p: ApiPlayer
        for p in players:
            blue = (saltie_game.data_frame[p]['pos_x'] < 0).sum()
            orange = (saltie_game.data_frame[p]['pos_x'] > 0).sum()
            players[p] = [blue / (blue + orange), orange / (blue + orange)]
        return players

    @staticmethod
    def get_player_speeds(saltie_game: 'SaltieGame'):
        players = {p.name: 0.0 for p in
                   (saltie_game.api_game.teams[0].players + saltie_game.api_game.teams[1].players)}
        p: ApiPlayer
        for p in players:
            pdf = saltie_game.data_frame[p]
            speed = np.sqrt(pdf.vel_x ** 2 + pdf.vel_y ** 2 + pdf.vel_z ** 2).mean()
            players[p] = speed

        return players
