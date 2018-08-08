# noinspection PyPep8Naming
class ApiPlayerCameraSettings:

    def __init__(self, stiffness: float = None, height: float = None, transitionSpeed: float = None,
                 pitch: float = None, swivelSpeed: float = None, fieldOfView: float = None, distance: float = None):
        self.stiffness = stiffness
        self.height = height
        self.transitionSpeed = transitionSpeed
        self.pitch = pitch
        self.swivelSpeed = swivelSpeed
        self.fieldOfView = fieldOfView
        self.distance = distance

    @staticmethod
    def create_from_player(player):
        player_camera_settings = player.camera_settings
        return ApiPlayerCameraSettings(
            stiffness=player_camera_settings['stiffness'],
            height=player_camera_settings['height'],
            transitionSpeed=player_camera_settings['transition_speed'],
            pitch=player_camera_settings['pitch'],
            swivelSpeed=player_camera_settings['swivel_speed'],
            fieldOfView=player_camera_settings['field_of_view'],
            distance=player_camera_settings['distance'],
        )
