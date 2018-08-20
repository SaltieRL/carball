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
    def create_from_player(proto_loadout, player):
        try:
            loadout = player.loadout[player.is_orange]
        except IndexError:
            return
        if player.camera_settings['banner'] is None:
            return

        proto_loadout.banner = loadout['banner']
        proto_loadout.boost = loadout['boost']
        proto_loadout.car = loadout['car']
        proto_loadout.goal_explosion = loadout['goal_explosion']
        proto_loadout.skin = loadout['skin']
        proto_loadout.trail = loadout['trail']
        proto_loadout.version = loadout['version']
        proto_loadout.wheels = loadout['wheels']
