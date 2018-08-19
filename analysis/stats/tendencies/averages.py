from typing import TYPE_CHECKING, List

import pandas as pd

if TYPE_CHECKING:
    from ...saltie_game.saltie_hit import SaltieHit
    from ...saltie_game.saltie_game import SaltieGame
    from ...saltie_game.metadata.ApiPlayer import ApiPlayer


class Averages:
    def __init__(self,
                 average_speed: float,
                 average_hit_distance: float,
                 ):
        self.average_speed = average_speed
        self.average_hit_distance = average_hit_distance

    def __repr__(self):
        return str(self.__dict__)

    @classmethod
    def get_averages_for_player(cls, player: 'ApiPlayer', saltie_game: 'SaltieGame'):
        goal_frames = saltie_game.data_frame.game.goal_number.notnull()
        player_dataframe = saltie_game.data_frame[player.name][goal_frames]

        speed: pd.Series = (
                                   player_dataframe.vel_x ** 2 + player_dataframe.vel_y ** 2 + player_dataframe.vel_z ** 2) ** 0.5
        average_speed = speed.mean()

        player_hits: List['SaltieHit'] = [saltie_hit for saltie_hit in saltie_game.saltie_hits.values() if
                                          saltie_hit.hit.player.name == player.name]

        hit_distances = [saltie_hit.distance for saltie_hit in player_hits
                         if saltie_hit.distance is not None and not saltie_hit.dribble]
        average_hit_distance = sum(hit_distances) / len(hit_distances)

        return cls(average_speed=average_speed, average_hit_distance=average_hit_distance)
