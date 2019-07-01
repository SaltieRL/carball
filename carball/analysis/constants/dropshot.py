from typing import Dict, Optional

# taken from https://github.com/RLBot/RLBot/wiki/Dropshot

TILE_DIAMETER = 886.82

CORE_707_TILES_POSITIONS = (
    # BLUE
    (2304.0, -4117.4287109375, 2.5),
    (1536.0, -4117.4287109375, 2.5),
    (768.0, -4117.4287109375, 2.5),
    (-0.0, -4117.4287109375, 2.5),
    (-768.0, -4117.4287109375, 2.5),
    (-1536.0, -4117.4287109375, 2.5),
    (-2304.0, -4117.4287109375, 2.5),
    (2688.0, -3452.322021484375, 2.5),
    (1920.0, -3452.322021484375, 2.5),
    (1152.0, -3452.322021484375, 2.5),
    (384.0, -3452.322021484375, 2.5),
    (-384.0, -3452.322021484375, 2.5),
    (-1152.0, -3452.322021484375, 2.5),
    (-1920.0, -3452.322021484375, 2.5),
    (-2688.0, -3452.322021484375, 2.5),
    (3072.0, -2788.428955078125, 2.5),
    (2304.0, -2788.428955078125, 2.5),
    (1536.0, -2788.428955078125, 2.5),
    (768.0, -2788.428955078125, 2.5),
    (-0.0, -2788.428955078125, 2.5),
    (-768.0, -2788.428955078125, 2.5),
    (-1536.0, -2788.428955078125, 2.5),
    (-2304.0, -2788.428955078125, 2.5),
    (-3072.0, -2788.428955078125, 2.5),
    (3456.0, -2123.322021484375, 2.5),
    (2688.0, -2123.322021484375, 2.5),
    (1920.0, -2123.322021484375, 2.5),
    (1152.0, -2123.322021484375, 2.5),
    (384.0, -2123.322021484375, 2.5),
    (-384.0, -2123.322021484375, 2.5),
    (-1152.0, -2123.322021484375, 2.5),
    (-1920.0, -2123.322021484375, 2.5),
    (-2688.0, -2123.322021484375, 2.5),
    (-3456.0, -2123.322021484375, 2.5),
    (3840.0, -1458.21484375, 2.5),
    (3072.0, -1458.21484375, 2.5),
    (2304.0, -1458.21484375, 2.5),
    (1536.0, -1458.21484375, 2.5),
    (768.0, -1458.21484375, 2.5),
    (-0.0, -1458.21484375, 2.5),
    (-768.0, -1458.21484375, 2.5),
    (-1536.0, -1458.21484375, 2.5),
    (-2304.0, -1458.21484375, 2.5),
    (-3072.0, -1458.21484375, 2.5),
    (-3840.0, -1458.21484375, 2.5),
    (4224.0, -793.1079711914062, 2.5),
    (3456.0, -793.1079711914062, 2.5),
    (2688.0, -793.1079711914062, 2.5),
    (1920.0, -793.1079711914062, 2.5),
    (1152.0, -793.1079711914062, 2.5),
    (384.0, -793.1079711914062, 2.5),
    (-384.0, -793.1079711914062, 2.5),
    (-1152.0, -793.1079711914062, 2.5),
    (-1920.0, -793.1079711914062, 2.5),
    (-2688.0, -793.1079711914062, 2.5),
    (-3456.0, -793.1079711914062, 2.5),
    (-4224.0, -793.1079711914062, 2.5),
    (4608.0, -127.99998474121094, 2.5),
    (3840.0, -127.99998474121094, 2.5),
    (3072.0, -127.99998474121094, 2.5),
    (2304.0, -127.99998474121094, 2.5),
    (1536.0, -127.99998474121094, 2.5),
    (768.0, -127.99998474121094, 2.5),
    (-0.0, -127.99998474121094, 2.5),
    (-768.0, -127.99998474121094, 2.5),
    (-1536.0, -127.99998474121094, 2.5),
    (-2304.0, -128.0, 2.5),
    (-3072.0, -127.99998474121094, 2.5),
    (-3840.0, -127.99998474121094, 2.5),
    (-4608.0, -127.99998474121094, 2.5),

    # ORANGE
    (4608.0, 128.0, 2.5),
    (3840.0, 128.0, 2.5),
    (3072.0, 128.0, 2.5),
    (2304.0, 128.0, 2.5),
    (1536.0, 128.0, 2.5),
    (768.0, 128.0, 2.5),
    (-0.0, 128.0, 2.5),
    (-768.0, 128.0, 2.5),
    (-1536.0, 128.0, 2.5),
    (-2304.0, 128.0, 2.5),
    (-3072.0, 128.0, 2.5),
    (-3840.0, 128.0, 2.5),
    (-4608.0, 128.0, 2.5),
    (4224.0, 793.1079711914062, 2.5),
    (3456.0, 793.1079711914062, 2.5),
    (2688.0, 793.1079711914062, 2.5),
    (1920.0, 793.1079711914062, 2.5),
    (1152.0, 793.1079711914062, 2.5),
    (384.0, 793.1079711914062, 2.5),
    (-384.0, 793.1079711914062, 2.5),
    (-1152.0, 793.1079711914062, 2.5),
    (-1920.0, 793.1079711914062, 2.5),
    (-2688.0, 793.1079711914062, 2.5),
    (-3456.0, 793.1079711914062, 2.5),
    (-4224.0, 793.1079711914062, 2.5),
    (3840.0, 1458.21484375, 2.5),
    (3072.0, 1458.21484375, 2.5),
    (2304.0, 1458.21484375, 2.5),
    (1536.0, 1458.21484375, 2.5),
    (768.0, 1458.21484375, 2.5),
    (-0.0, 1458.21484375, 2.5),
    (-768.0, 1458.21484375, 2.5),
    (-1536.0, 1458.21484375, 2.5),
    (-2304.0, 1458.21484375, 2.5),
    (-3072.0, 1458.21484375, 2.5),
    (-3840.0, 1458.21484375, 2.5),
    (3456.0, 2123.322021484375, 2.5),
    (2688.0, 2123.322021484375, 2.5),
    (1920.0, 2123.322021484375, 2.5),
    (1152.0, 2123.322021484375, 2.5),
    (384.0, 2123.322021484375, 2.5),
    (-384.0, 2123.322021484375, 2.5),
    (-1152.0, 2123.322021484375, 2.5),
    (-1920.0, 2123.322021484375, 2.5),
    (-2688.0, 2123.322021484375, 2.5),
    (-3456.0, 2123.322021484375, 2.5),
    (3072.0, 2788.428955078125, 2.5),
    (2304.0, 2788.428955078125, 2.5),
    (1536.0, 2788.428955078125, 2.5),
    (768.0, 2788.428955078125, 2.5),
    (-0.0, 2788.428955078125, 2.5),
    (-768.0, 2788.428955078125, 2.5),
    (-1536.0, 2788.428955078125, 2.5),
    (-2304.0, 2788.428955078125, 2.5),
    (-3072.0, 2788.428955078125, 2.5),
    (2688.0, 3452.322021484375, 2.5),
    (1920.0, 3452.322021484375, 2.5),
    (1152.0, 3452.322021484375, 2.5),
    (384.0, 3452.322021484375, 2.5),
    (-384.0, 3452.322021484375, 2.5),
    (-1152.0, 3452.322021484375, 2.5),
    (-1920.0, 3452.322021484375, 2.5),
    (-2688.0, 3452.322021484375, 2.5),
    (2304.0, 4117.4287109375, 2.5),
    (1536.0, 4117.4287109375, 2.5),
    (768.0, 4117.4287109375, 2.5),
    (-0.0, 4117.4287109375, 2.5),
    (-768.0, 4117.4287109375, 2.5),
    (-1536.0, 4117.4287109375, 2.5),
    (-2304.0, 4117.4287109375, 2.5)
)

_MAPPING = {
    'ShatterShot_P': CORE_707_TILES_POSITIONS
}


def get_tile_positions(map_name: str) -> Optional[Dict[int, int]]:
    return _MAPPING.get(map_name, None)
