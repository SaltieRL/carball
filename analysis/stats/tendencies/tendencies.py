from ..player_tendencies import PlayerTendencies as PT


class TendenciesStat:
    def __init__(self, player_tendencies):
        self.player_tendencies = player_tendencies

    @classmethod
    def get_tendencies(cls, game) -> 'TendenciesStat':
        player_tendencies = {
            player: PT.get_player_tendencies(game.goal_data_frame[player.name], game) for player in game.players
        }
        return cls(player_tendencies)
