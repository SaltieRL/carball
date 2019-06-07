from .base import *


class PlatformHandler(BaseActorHandler):

    def __init__(self, parser: object):
        super().__init__(parser)

    @classmethod
    def can_handle(cls, actor: dict) -> bool:
        return actor['ClassName'] == 'TAGame.BreakOutActor_Platform_TA' and \
               actor['Name'].startswith('BreakOutActor_Platform_TA_')

    def update(self, actor: dict, frame_number: int, time: float, delta: float) -> None:
        tile_id = int(actor['TypeName'][actor['TypeName'].rfind('_') + 1:])

        if tile_id not in self.parser.dropshot['tile_states']:
            self.parser.dropshot['tile_states'][tile_id] = 0

        damage_state = actor['TAGame.BreakOutActor_Platform_TA:DamageState']['damage_state']

        if tile_id not in self.parser.dropshot['tiles']:
            self.parser.dropshot['tiles'][tile_id] = {}

        # unknown1: 0 - undamaged, 1 - damaged, 2 - destroyed
        state = damage_state['unknown1']

        # unknown2: False when undamaged, True otherwise?

        # unknown3: damaging player actor id
        player_actor_id = damage_state['unknown3']

        # unknown4: (size, bias, x, y, z) properties that have a value of (0, 2, 0, 0, 0) when the tile is undamaged
        # probably the position of the ball when the tile was damaged as tiles in the same event have the same value

        # unknown5: In a single damage event only one tile has a value of True, the others are False
        # probably the center of the damage aka the tile that was hit

        # unknown6: seems to be always False

        if state > self.parser.dropshot['tile_states'][tile_id]:

            if frame_number not in self.parser.dropshot['damage_events']:
                self.parser.dropshot['damage_events'][frame_number] = (player_actor_id, [])

            self.parser.dropshot['damage_events'][frame_number][1].append((tile_id, state))

        self.parser.dropshot['tile_states'][tile_id] = state

        # TODO remove this
        self.parser.dropshot['tiles'][tile_id][frame_number] = {
            'unknown1': damage_state['unknown1'],
            'unknown2': damage_state['unknown2'],
            'unknown3': damage_state['unknown3'],
            'size': damage_state['unknown4']['size']['value'],
            'bias': damage_state['unknown4']['bias'],
            'x': damage_state['unknown4']['x'],
            'y': damage_state['unknown4']['y'],
            'z': damage_state['unknown4']['z'],
            'unknown5': damage_state['unknown5'],
            'unknown6': damage_state['unknown6']
        }
