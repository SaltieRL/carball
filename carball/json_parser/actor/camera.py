from .base import *


class CameraSettingsHandler(BaseActorHandler):
    type_name = 'TAGame.Default__CameraSettingsActor_TA'

    def update(self, actor: dict, frame_number: int, time: float, delta: float) -> None:
        if 'TAGame.CameraSettingsActor_TA:PRI' not in actor:
            return

        player_actor_id = actor['TAGame.CameraSettingsActor_TA:PRI']['actor']  # may need to try another key
        # add camera settings
        if player_actor_id not in self.parser.cameras_data and \
                'TAGame.CameraSettingsActor_TA:ProfileSettings' in actor:
            self.parser.cameras_data[player_actor_id] = actor['TAGame.CameraSettingsActor_TA:ProfileSettings']
        # add ball cam to inputs
        ball_cam = actor.get('TAGame.CameraSettingsActor_TA:bUsingSecondaryCamera', None)
        try:
            self.parser.player_data[player_actor_id][frame_number]['ball_cam'] = ball_cam
        except KeyError:
            # key error due to frame_number not in inputs
            # ignore as no point knowing
            pass
