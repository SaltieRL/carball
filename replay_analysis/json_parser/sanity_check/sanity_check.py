import logging
from typing import List, Type

from json_parser.game import Game
from .base_checks.base_check import BaseCheck
from .base_checks.game_check import GameCheck
from .base_checks.player_check import PlayerCheck
from .checks.ball_dataframe import BallDataFrameCheck
from .checks.player_attributes import PlayerAttributesCheck
from .checks.player_dataframe import PlayerDataFrameCheck
from .errors.errors import CheckErrorLevel, CheckError

logger = logging.getLogger(__name__)

CHECKS_TO_RUN: List[Type[BaseCheck]] = [
    BallDataFrameCheck,
    PlayerAttributesCheck,
    PlayerDataFrameCheck,
]


def check_game(game: Game, failing_level: CheckErrorLevel = CheckErrorLevel.CRITICAL):
    errors: List[CheckError] = []

    for check in CHECKS_TO_RUN:
        logger.info(f'Running check: {check.__name__}')
        if issubclass(check, PlayerCheck):
            for player in game.players:
                errors += check(player).run_check()
        elif issubclass(check, GameCheck):
            errors += check(game).run_check()

    for error in errors:
        if error.level.value >= failing_level.value:
            raise error

    logger.info('All checks passed.')
