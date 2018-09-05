import logging

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game import Game
    from .player import Player

logger = logging.getLogger(__name__)


class Goal:

    def __init__(self, goal_dict, game: 'Game'):
        # self.time = goal_dict["Time"]
        self.player_name = goal_dict["PlayerName"]['value']['str']
        self.player_team = goal_dict["PlayerTeam"]['value']['int']

        self.player = self.get_player(game)
        self.frame_number = goal_dict["frame"]["value"]["int"]
        logger.info('Created Goal: %s' % self)

    def __repr__(self):
        if self.player:
            return "Goal by %s on frame %s" % (self.player.name, self.frame_number)
        else:
            return "Goal by unknown player with name %s on frame %s" % (self.player_name, self.frame_number)

    def get_player(self, game: 'Game') -> 'Player':
        for player in game.players:
            if player.name == self.player_name:
                return player
