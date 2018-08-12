from .ApiPlayerCameraSettings import ApiPlayerCameraSettings
from .ApiPlayerLoadout import ApiPlayerLoadout


# noinspection PyPep8Naming
class ApiPlayer:

    def __init__(self, id_: str = None, name: str = None, steamProfile: str = None,
                 titleId: int = None,
                 matchScore: int = None,
                 matchGoals: int = None,
                 matchAssists: int = None,
                 matchSaves: int = None,
                 matchShots: int = None,
                 cameraSettings: ApiPlayerCameraSettings = None,
                 loadout: ApiPlayerLoadout = None,
                 isOrange: bool = None
                 ):
        self.id = id_
        self.name = name
        self.titleId = titleId
        self.matchScore = matchScore
        self.matchGoals = matchGoals
        self.matchAssists = matchAssists
        self.matchSaves = matchSaves
        self.matchShots = matchShots
        self.cameraSettings = cameraSettings
        self.loadout = loadout
        self.isOrange = isOrange

    @staticmethod
    def create_from_player(player):
        camera_settings = ApiPlayerCameraSettings.create_from_player(player)
        loadout = ApiPlayerLoadout.create_from_player(player)
        # TODO: Add support for detecting xbox player ids.
        return ApiPlayer(id_=player.online_id,
                         name=player.name,
                         titleId=player.title,
                         matchScore=player.score,
                         matchGoals=player.goals,
                         matchAssists=player.assists,
                         matchSaves=player.saves,
                         matchShots=player.shots,
                         cameraSettings=camera_settings,
                         loadout=loadout,
                         isOrange=player.is_orange
                         )
