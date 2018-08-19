from typing import List


class ApiDemo:

    def __init__(self,
                 frame: float,
                 attacker: str = None,
                 victim: str = None
                 ):
        self.frame = frame
        self.attacker = attacker
        self.victim = victim

    def __str__(self):
        return "Demo on %s by %s on frame %s" % (self.victim, self.attacker, self.frame)

    @classmethod
    def create_demos_from_game(cls, game) -> List['ApiDemo']:
        demos = []
        for _demo in game.demos:
            demos.append(
                cls(
                    frame=_demo['frame_number'],
                    attacker=_demo['attacker'],
                    victim=_demo['victim']
                )
            )
        return demos
