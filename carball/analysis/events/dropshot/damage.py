from carball.json_parser.game import Game
from carball.generated.api import game_pb2
from carball.generated.api.metadata.game_metadata_pb2 import RANKED_DROPSHOT, UNRANKED_DROPSHOT


def create_dropshot_damage_events(game: Game, proto_game: game_pb2.Game):
    if game.game_info.playlist not in [RANKED_DROPSHOT, UNRANKED_DROPSHOT] and game.map != 'ShatterShot_P':
        return

    proto_damages = proto_game.game_stats.dropshot_stats.damage_events

    for event in game.dropshot['damage_events']:
        proto_damage_event = proto_damages.add()
        proto_damage_event.frame_number = event['frame_number']
        proto_damage_event.player_id.id = str(event['player'].online_id)

        for tile in event['tiles']:
            proto_tile = proto_damage_event.tiles.add()
            proto_tile.id = tile[0]
            proto_tile.state = tile[1]

            if tile[2]:
                proto_damage_event.tile_hit = tile[0]
