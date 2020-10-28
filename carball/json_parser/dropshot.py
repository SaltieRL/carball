from typing import Dict, Optional

CORE_707_MAPPING = {
    # BLUE
    178: 0,
    222: 1,
    221: 2,
    218: 3,
    219: 4,
    220: 5,
    173: 6,
    214: 7,
    215: 8,
    216: 9,
    217: 10,
    206: 11,
    207: 12,
    208: 13,
    209: 14,
    155: 15,
    154: 16,
    153: 17,
    152: 18,
    147: 19,
    148: 20,
    149: 21,
    150: 22,
    151: 23,
    213: 24,
    143: 25,
    144: 26,
    145: 27,
    146: 28,
    138: 29,
    139: 30,
    140: 31,
    141: 32,
    142: 33,
    99: 34,
    204: 35,
    203: 36,
    202: 37,
    199: 38,
    192: 39,
    193: 40,
    195: 41,
    196: 42,
    197: 43,
    29: 44,
    101: 45,
    98: 46,
    188: 47,
    189: 48,
    190: 49,
    191: 50,
    180: 51,
    181: 52,
    182: 53,
    183: 54,
    25: 55,
    93: 56,
    42: 57,
    97: 58,
    17: 59,
    16: 60,
    14: 61,
    1: 62,
    169: 63,
    20: 64,
    21: 65,
    22: 66,
    23: 67,
    9: 68,
    92: 69,

    # ORANGE
    32: 70,
    94: 71,
    31: 72,
    28: 73,
    27: 74,
    18: 75,
    227: 76,
    10: 77,
    11: 78,
    12: 79,
    13: 80,
    4: 81,
    90: 82,
    100: 83,
    95: 84,
    36: 85,
    35: 86,
    34: 87,
    33: 88,
    45: 89,
    44: 90,
    43: 91,
    41: 92,
    5: 93,
    91: 94,
    96: 95,
    51: 96,
    50: 97,
    48: 98,
    47: 99,
    46: 100,
    53: 101,
    54: 102,
    55: 103,
    56: 104,
    6: 105,
    106: 106,
    105: 107,
    104: 108,
    103: 109,
    102: 110,
    110: 111,
    109: 112,
    108: 113,
    107: 114,
    65: 115,
    115: 116,
    114: 117,
    113: 118,
    112: 119,
    111: 120,
    116: 121,
    117: 122,
    118: 123,
    119: 124,
    61: 125,
    60: 126,
    59: 127,
    58: 128,
    69: 129,
    68: 130,
    67: 131,
    66: 132,
    73: 133,
    72: 134,
    71: 135,
    70: 136,
    76: 137,
    77: 138,
    78: 139
}

_MAPPING = {
    'ShatterShot_P': CORE_707_MAPPING
}


def get_tile_mapping(map_name: str) -> Optional[Dict[int, int]]:
    return _MAPPING.get(map_name, None)