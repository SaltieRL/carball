class ApiPlayerLoadout:

    @staticmethod
    def create_from_player(proto_loadout, player):
        try:
            loadout = player.loadout[player.is_orange]
        except IndexError:
            return

        if loadout['banner'] is not None:
            proto_loadout.banner = loadout['banner']
        if loadout['boost'] is not None:
            proto_loadout.boost = loadout['boost']
        if loadout['car'] is not None:
            proto_loadout.car = loadout['car']
        if loadout['goal_explosion'] is not None:
            proto_loadout.goal_explosion = loadout['goal_explosion']
        if loadout['skin'] is not None:
            proto_loadout.skin = loadout['skin']
        if loadout['trail'] is not None:
            proto_loadout.trail = loadout['trail']
        if loadout['version'] is not None:
            proto_loadout.version = loadout['version']
        if loadout['wheels'] is not None:
            proto_loadout.wheels = loadout['wheels']
        if loadout['topper'] is not None:
            proto_loadout.topper = loadout['topper']
        if loadout['antenna'] is not None:
            proto_loadout.antenna = loadout['antenna']
        if loadout['engine_audio'] is not None:
            proto_loadout.engine_audio = loadout['engine_audio']
