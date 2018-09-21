import logging
import time

import pandas as pd

from carball.json_parser.game import Game
from .rotations import predict_user_inputs

# RETURNS CONTROLS
# THROTTLE STEER PITCH YAW ROLL JUMP BOOST HANDBRAKE

logger = logging.getLogger(__name__)


class ControlsCreator:

    def get_controls(self, game: Game):
        logger.info('Creating controls')
        start_time = time.time()
        for player in game.players:
            logger.debug('getting controls for player %s', player.name)
            throttle = player.data.throttle / 128 - 1
            steer = -(player.data.steer / 128 - 1)

            _jump = player.data.jump_active % 2 == 1
            _double_jump_active = player.data.double_jump_active % 2 == 1
            _dodge_active = player.data.dodge_active % 2 == 1
            jump = _jump | _double_jump_active | _dodge_active
            boost = player.data.boost_active
            handbrake = player.data.handbrake

            frames_not_on_ground = player.data.loc[:, 'pos_z'][player.data.loc[:, 'pos_z'] > 18].index.values
            # print(frames_not_on_ground)
            rotations = player.data.loc[frames_not_on_ground, ['rot_x', 'rot_y', 'rot_z']]
            ang_vels = player.data.loc[frames_not_on_ground, ['ang_vel_x', 'ang_vel_y', 'ang_vel_z']] / 1000

            predicted_inputs = predict_user_inputs(ang_vels, rotations, game.frames.delta)
            # print(predicted_inputs)
            pitch = predicted_inputs.loc[:, 'predicted_input_pitch']
            yaw = predicted_inputs.loc[:, 'predicted_input_yaw']
            roll = predicted_inputs.loc[:, 'predicted_input_roll']

            # rotations = pd.concat((player.data.pos_z, player.data.loc[frames_not_on_ground, 'rot_x':'rot_z'],
            #                        predicted_inputs), axis=1)

            player.controls = pd.DataFrame.from_dict({'throttle': throttle, 'steer': steer, 'pitch': pitch, 'yaw': yaw,
                                                      'roll': roll, 'jump': jump, 'boost': boost,
                                                      'handbrake': handbrake})

        logger.info('Finished controls in %s seconds', str(time.time() - start_time))
        return
