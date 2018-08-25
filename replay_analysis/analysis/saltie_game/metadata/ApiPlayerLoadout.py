class ApiPlayerLoadout:

    @staticmethod
    def create_from_player(proto_loadout, player):
        try:
            loadout = player.loadout[player.is_orange]
        except IndexError:
            return
        if loadout['banner'] is None:
            return

        proto_loadout.banner = loadout['banner']
        proto_loadout.boost = loadout['boost']
        proto_loadout.car = loadout['car']
        proto_loadout.goal_explosion = loadout['goal_explosion']
        proto_loadout.skin = loadout['skin']
        proto_loadout.trail = loadout['trail']
        proto_loadout.version = loadout['version']
        proto_loadout.wheels = loadout['wheels']
