from typing import List, Optional

from ..base_checks.game_check import GameCheck


class BallDataFrameCheck(GameCheck):
    class_message = "All columns in ball dataframe must have at least 1 truthy value."

    def critical_checks(self) -> List[Optional[AssertionError]]:
        ball = self.obj.ball
        return [
            self.check(ball.any(axis=0).all(), 'ball data frame columns have truthy values')
        ]
