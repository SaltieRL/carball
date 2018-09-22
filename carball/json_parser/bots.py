import hashlib
import logging

bots = [
    "Armstrong",
    "Bandit",
    "Beast",
    "Boomer",
    "Buzz",
    "Casper",
    "Caveman",
    "C-Block",
    "Centice",
    "Chipper",
    "Cougar",
    "Dude",
    "Foamer",
    "Fury",
    "Gerwin",
    "Goose",
    "Heater",
    "Hollywood",
    "Hound",
    "Iceman",
    "Imp",
    "Jester",
    "JM",
    "Junker",
    "Khan",
    "Maverick",
    "Middy",
    "Merlin",
    "Mountain",
    "Myrtle",
    "Outlaw",
    "Poncho",
    "Rainmaker",
    "Raja",
    "Rex",
    "Roundhouse",
    "Sabretooth",
    "Saltie",
    "Samara",
    "Scout",
    "Shepard",
    "Slider",
    "Squall",
    "Sticks",
    "Stinger",
    "Storm",
    "Sundown",
    "Sultan",
    "Swabbie",
    "Tusk",
    "Tex",
    "Viper",
    "Wolfman",
    "Yuri",
]

logger = logging.getLogger(__name__)


def h11(w):
    return hashlib.md5(w).hexdigest()[:9]


def get_bot_map():
    result = dict()
    for i in range(len(bots)):
        result[bots[i]] = i + 1
    return result


def get_online_id_for_bot(bot_map, player):
    try:
        return 'b' + str(bot_map[player.name]) + 'b'
    except:
        logger.warning('Found bot not in bot list')
        try:
            return 'b' + h11(str(player.name).encode('utf-8').lower()) + 'b'
        except:
            logger.warning('bot has invalid name')
            return 'invalid_name'

