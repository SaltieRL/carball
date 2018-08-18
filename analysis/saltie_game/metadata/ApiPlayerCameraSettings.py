class ApiPlayerCameraSettings:

    def __init__(self, stiffness: float = None, height: float = None, transition_speed: float = None,
                 pitch: float = None, swivel_speed: float = None, field_of_view: float = None, distance: float = None):
        self.stiffness = stiffness
        self.height = height
        self.transition_speed = transition_speed
        self.pitch = pitch
        self.swivel_speed = swivel_speed
        self.field_of_view = field_of_view
        self.distance = distance

    @staticmethod
    def create_from_player(player):
        player_camera_settings = player.camera_settings
        return ApiPlayerCameraSettings(
            stiffness=player_camera_settings['stiffness'],
            height=player_camera_settings['height'],
            transition_speed=player_camera_settings['transition_speed'],
            pitch=player_camera_settings['pitch'],
            swivel_speed=player_camera_settings['swivel_speed'],
            field_of_view=player_camera_settings['field_of_view'],
            distance=player_camera_settings['distance'],
        )
