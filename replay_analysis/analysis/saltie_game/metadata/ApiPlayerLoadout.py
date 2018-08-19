class ApiPlayerLoadout:

    def __init__(self, banner: int = None, boost: int = None, car: int = None, goal_explosion: int = None,
                 skin: int = None, trail: int = None, version: int = None, wheels: int = None):
        self.banner = banner
        self.boost = boost
        self.car = car
        self.goal_explosion = goal_explosion
        self.skin = skin
        self.trail = trail
        self.wheels = wheels
        self.version = version

    @staticmethod
    def create_from_player(player):
        try:
            loadout = player.loadout[player.is_orange]
        except IndexError:
            loadout = player.loadout[0]

        return ApiPlayerLoadout(
            banner=loadout['banner'],
            boost=loadout['boost'],
            car=loadout['car'],
            goal_explosion=loadout['goal_explosion'],
            skin=loadout['skin'],
            trail=loadout['trail'],
            version=loadout['version'],
            wheels=loadout['wheels'],
        )
