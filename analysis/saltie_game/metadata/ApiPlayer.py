from .ApiPlayerCameraSettings import ApiPlayerCameraSettings
from .ApiPlayerLoadout import ApiPlayerLoadout


# noinspection PyPep8Naming
class ApiPlayer:

    def __init__(self, _id: int = None, name: str = None, steamProfile: str = None,
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
        self.id = _id
        self.name = name
        self.steamProfile = steamProfile
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
        return ApiPlayer(_id=player.online_id,
                         name=player.name,
                         steamProfile='https://steamcommunity.com/profiles/' + player.online_id,
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
