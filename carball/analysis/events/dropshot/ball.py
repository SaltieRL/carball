import logging
from typing import Dict
from carball.json_parser.game import Game
from carball.generated.api import game_pb2
from carball.generated.api.game_pb2 import mutators_pb2 as mutators
from carball.generated.api.player_pb2 import Player

log = logging.getLogger(__name__)


def create_dropshot_ball_events(game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player]):
    if game.ball_type != mutators.BREAKOUT:
        return

    hits = list(proto_game.game_stats.hits)
    proto_events = proto_game.game_stats.dropshot_stats.ball_phase_events
    for event in game.dropshot['ball_events']:

        frame_number = event['frame_number']
        proto_event = proto_events.add()
        proto_event.frame_number = frame_number
        proto_event.ball_phase = event['state']

        while len(hits) > 1 and hits[1].frame_number <= frame_number:
            hits.pop(0)

        hit = hits.pop(0)

        if hit.frame_number != frame_number:
            log.warning(f'Did not find exact hit event for dropshot ball event at frame {frame_number}, hit frame {hit.frame_number}')

        player = player_map[hit.player_id.id]

        if player.is_orange != bool(event['team']):
            log.warning(f'Team does not match in dropshot ball event ({frame_number}) and hit event ({hit.frame_number})')
            return

        proto_event.player_id.id = player.id.id
