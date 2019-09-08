class ApiPlayerLoadout:

    @staticmethod
    def create_from_player(proto_loadout, player):
        try:
            loadout = player.loadout[player.is_orange]
            paints = player.paint[player.is_orange]
            user_colors = player.user_colors[player.is_orange]
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
        if loadout['avatar_border'] is not None:
            proto_loadout.engine_audio = loadout['avatar_border']

        if paints['banner'] is not None:
            proto_loadout.banner_paint = paints['banner']
        if paints['boost'] is not None:
            proto_loadout.boost_paint = paints['boost']
        if paints['car'] is not None:
            proto_loadout.car_paint = paints['car']
        if paints['goal_explosion'] is not None:
            proto_loadout.goal_explosion_paint = paints['goal_explosion']
        if paints['skin'] is not None:
            proto_loadout.skin_paint = paints['skin']
        if paints['trail'] is not None:
            proto_loadout.trail_paint = paints['trail']
        if paints['wheels'] is not None:
            proto_loadout.wheels_paint = paints['wheels']
        if paints['topper'] is not None:
            proto_loadout.topper_paint = paints['topper']
        if paints['antenna'] is not None:
            proto_loadout.antenna_paint = paints['antenna']

        if loadout['primary_color'] is not None:
            proto_loadout.primary_color = loadout['primary_color']
        if loadout['accent_color'] is not None:
            proto_loadout.accent_color = loadout['accent_color']
        if loadout['primary_finish'] is not None:
            proto_loadout.primary_finish = loadout['primary_finish']
        if loadout['accent_finish'] is not None:
            proto_loadout.accent_finish = loadout['accent_finish']

        if user_colors['banner'] is not None:
            proto_loadout.banner_user_color = user_colors['banner']
        if user_colors['avatar_border'] is not None:
            proto_loadout.avatar_border_user_color = user_colors['avatar_border']
