from typing import Optional

from ....json_parser.player import Player
from .base_check import BaseCheck


class PlayerCheck(BaseCheck[Player]):

    def check(self, condition: bool, message: str) -> Optional[AssertionError]:
        return super().check(condition, f'{message} ({self.obj.name})')
