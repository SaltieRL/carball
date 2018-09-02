from typing import List, ClassVar, Optional

from ..base_checks.player_check import PlayerCheck


class PlayerAttributesCheck(PlayerCheck):
    class_message: ClassVar[str] = "Player attributes must be set"

    def critical_checks(self) -> List[Optional[AssertionError]]:
        player = self.obj
        return [
            self.check(player.is_orange is not None, 'is_orange is not None'),
            self.check(player.online_id is not None, 'online_id is not None'),
            self.check(player.team is not None, 'team is not None'),
            self.check(player.name is not None, 'name is not None'),
        ]

    def major_checks(self) -> List[Optional[AssertionError]]:
        player = self.obj
        return [
                   self.check(any(player.camera_settings.values()), 'camera_settings has at least 1 value')
               ] + [
                   self.check(all(isinstance(value, int) for value in loadout.values()), 'all loadouts are ints')
                   for loadout in player.loadout
               ]
