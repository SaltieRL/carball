from typing import List, Optional

from ..base_checks.game_check import GameCheck


class BallDataFrameCheck(GameCheck):
    class_message = "All columns in ball data frame must have at least 1 truthy value."

    def critical_checks(self) -> List[Optional[AssertionError]]:
        ball = self.obj.ball
        return [
            self.check(condition, f'ball data frame column: {column_name} has truthy values')
            for column_name, condition in ball.any(axis=0).iteritems()
        ]
