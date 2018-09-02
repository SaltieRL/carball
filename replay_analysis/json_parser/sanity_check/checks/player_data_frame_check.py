from typing import ClassVar, List, Optional

from ..base_checks.player_check import PlayerCheck


class PlayerDataFrameCheck(PlayerCheck):
    class_message: ClassVar[str] = "All columns in player data frame must have at least 1 truthy value."

    def critical_checks(self) -> List[Optional[AssertionError]]:
        player = self.obj
        if player.data is not None:
            return [
                self.check(condition, f'player.data column: {column_name} has truthy values')
                for column_name, condition in player.data.any(axis=0).iteritems()
            ]
        else:
            return [
                self.check(False, 'player has non-None .data attribute')
            ]
