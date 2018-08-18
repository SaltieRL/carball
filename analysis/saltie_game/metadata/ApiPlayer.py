from .ApiPlayerCameraSettings import ApiPlayerCameraSettings
from .ApiPlayerLoadout import ApiPlayerLoadout


class ApiPlayer:

    def __init__(self, id_: str = None, name: str = None,
                 title_id: int = None,
                 score: int = None,
                 goals: int = None,
                 assists: int = None,
                 saves: int = None,
                 shots: int = None,
                 camera_settings: ApiPlayerCameraSettings = None,
                 loadout: ApiPlayerLoadout = None,
                 is_orange: bool = None
                 ):
        self.id = id_
        self.name = name
        self.title_id = title_id
        self.score = score
        self.goals = goals
        self.assists = assists
        self.saves = saves
        self.shots = shots
        self.camera_settings = camera_settings
        self.loadout = loadout
        self.is_orange = is_orange

    @staticmethod
    def create_from_player(player):
        camera_settings = ApiPlayerCameraSettings.create_from_player(player)
        loadout = ApiPlayerLoadout.create_from_player(player)
        # TODO: Add support for detecting xbox player ids.
        return ApiPlayer(id_=player.online_id,
                         name=player.name,
                         title_id=player.title,
                         score=player.score,
                         goals=player.goals,
                         assists=player.assists,
                         saves=player.saves,
                         shots=player.shots,
                         camera_settings=camera_settings,
                         loadout=loadout,
                         is_orange=player.is_orange
                         )
