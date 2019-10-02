from .base import *
from carball.json_parser.dropshot import get_tile_mapping


class PlatformHandler(BaseActorHandler):

    def __init__(self, parser: object):
        super().__init__(parser)

    @classmethod
    def can_handle(cls, actor: dict) -> bool:
        return actor['TypeName'].startswith('ShatterShot_VFX.TheWorld:PersistentLevel.BreakOutActor_Platform_TA_')

    def update(self, actor: dict, frame_number: int, time: float, delta: float) -> None:
        tile_id = int(actor['TypeName'][actor['TypeName'].rfind('_') + 1:])

        tile_mapping = get_tile_mapping(self.parser.game.map)
        if tile_mapping is not None:
            tile_id = tile_mapping[tile_id]

        if tile_id not in self.parser.dropshot['tile_states']:
            self.parser.dropshot['tile_states'][tile_id] = 0

        damage_state = actor['TAGame.BreakOutActor_Platform_TA:DamageState']['damage_state']

        # unknown1: 0 - undamaged, 1 - damaged, 2 - destroyed
        state = damage_state['unknown1']

        # unknown2: False when undamaged, True otherwise?

        # unknown3: damaging player actor id
        player_actor_id = damage_state['unknown3']

        # unknown4: (size, bias, x, y, z) properties that have a value of (0, 2, 0, 0, 0) when the tile is undamaged
        # probably the position of the ball when the tile was damaged as tiles in the same event have the same value

        # unknown5: In a single damage event only one tile has a value of True, the others are False
        # probably the center of the damage aka the tile that was hit
        tile_hit = damage_state['unknown5']

        # unknown6: seems to be always False

        if state > self.parser.dropshot['tile_states'][tile_id]:

            if frame_number not in self.parser.dropshot['damage_events']:
                self.parser.dropshot['damage_events'][frame_number] = (player_actor_id, [])

            self.parser.dropshot['damage_events'][frame_number][1].append((tile_id, state, tile_hit))

        self.parser.dropshot['tile_states'][tile_id] = state

        if frame_number not in self.parser.dropshot['tile_frames']:
            self.parser.dropshot['tile_frames'][frame_number] = {}
        self.parser.dropshot['tile_frames'][frame_number][tile_id] = state
        self.parser.frames_data[frame_number][f'dropshot_tile_{tile_id}'] = state
