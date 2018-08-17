from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from ...saltie_game.saltie_game import SaltieGame
    from ...hit_detection.base_hit import BaseHit


class TurnoverStat:
    def __init__(self, turnovers):
        self.turnovers = turnovers

    @classmethod
    def get_boost(cls, saltie_game: 'SaltieGame'):
        return cls(TurnoverStat.get_player_boost_usage(saltie_game))

    @staticmethod
    def get_player_boost_usage(saltie_game: 'SaltieGame'):
        turnovers = {p.name: 0 for p in (saltie_game.api_game.teams[0].players + saltie_game.api_game.teams[1].players)}
        hits = list(saltie_game.hits.values())  # type: List[BaseHit]
        for i in range(len(hits) - 2):
            if hits[i + 1].player.is_orange != hits[i].player.is_orange:
                if hits[i + 2].player.is_orange != hits[i].player.is_orange:
                    turnovers[hits[i].player.name] += 1
        return turnovers
