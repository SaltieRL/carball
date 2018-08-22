from typing import Dict

from replay_analysis.generated.api import game_pb2
from replay_analysis.generated.api.player_pb2 import Player
from replay_analysis.generated.api.stats.events_pb2 import Hit
from replay_analysis.generated.api.stats.player_stats_pb2 import PlayerStats
from replay_analysis.json_parser.game import Game

""""
if TYPE_CHECKING:
    from ..saltie_game.saltie_game import SaltieGame


def get_stats(saltie_game: 'SaltieGame') -> Dict:
    return {
        'tendencies': TendenciesStat.get_tendencies(saltie_game),
        'possession': PossessionStat.get_possession(saltie_game),
        'turnovers': TurnoverStat.get_player_turnovers(saltie_game),
        'boost': BoostStat.get_boost(saltie_game),
        'distance_hit_ball_forward': get_distance_hit_ball_forward(saltie_game)
    }
"""

class BaseStat:
    def calculate_stat(self, proto_stat, game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player],
                       data_frames):
        raise NotImplementedError()

    def calculate_player_stat(self, player_stat_map: Dict[str, PlayerStats], game: Game, proto_game: game_pb2.Game,
                              player_map: Dict[str, Player], data_frames):
        raise NotImplementedError()

    def calculate_team_stat(self, team_stat_list, game: Game, proto_game: game_pb2.Game,
                            player_map: Dict[str, Player], data_frames):
        raise NotImplementedError()


class HitStat:
    def calculate_next_stat(self, game: Game, saltie_hit: Hit, next_saltie_hit: Hit, player_map: Dict[str, Player]):
        raise NotImplementedError()
