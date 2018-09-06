import logging
from typing import List, Type

from .base_checks.base_check import BaseCheck
from .base_checks.game_check import GameCheck
from .base_checks.player_check import PlayerCheck
from .checks.ball_data_frame_check import BallDataFrameCheck
from .checks.player_attributes_check import PlayerAttributesCheck
from .checks.player_data_frame_check import PlayerDataFrameCheck
from .errors.errors import CheckErrorLevel, CheckError
from ...json_parser.game import Game

logger = logging.getLogger(__name__)

CHECKS_TO_RUN: List[Type[BaseCheck]] = [
    BallDataFrameCheck,
    PlayerAttributesCheck,
    PlayerDataFrameCheck,
]


class SanityChecker:
    """
    Checks the replays to make sure the data we are outputting are correct data.
    """

    def __init__(self, failing_level: CheckErrorLevel = CheckErrorLevel.CRITICAL):
        self.failing_level = failing_level

    def check_game(self, game: Game):
        errors: List[CheckError] = []

        for check in CHECKS_TO_RUN:
            logger.info(f'Running check: {check.__name__}')
            if issubclass(check, PlayerCheck):
                for player in game.players:
                    errors += check(player).run_check()
            elif issubclass(check, GameCheck):
                errors += check(game).run_check()

        for error in errors:
            if error.level.value >= self.failing_level.value:
                raise error

        logger.info('All checks passed.')
