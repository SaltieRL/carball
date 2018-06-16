import pandas as pd
from controls.rotations import predict_user_inputs
# RETURNS CONTROLS
# THROTTLE STEER PITCH YAW ROLL JUMP BOOST HANDBRAKE


def get_controls(game):
    for player in game.players:
        throttle = player.data.throttle / 128 - 1
        steer = player.data.steer / 128 - 1

        jump = player.data.loc[:, ['jump_active', 'double_jump_active', 'dodge_active']].any(axis=1)
        boost = player.data.boost_active
        handbrake = player.data.handbrake

        frames_not_on_ground = player.data.loc[:, 'pos_z'][player.data.loc[:, 'pos_z'] > 18].index.values
        # print(frames_not_on_ground)
        predicted_inputs = predict_user_inputs(player.data.loc[frames_not_on_ground, 'ang_vel_x':'ang_vel_z'] / 1000,
                                               player.data.loc[frames_not_on_ground, 'rot_x':'rot_z'])
        # print(predicted_inputs)
        pitch = predicted_inputs.loc[:, 'predicted_input_pitch']
        yaw = predicted_inputs.loc[:, 'predicted_input_yaw']
        roll = predicted_inputs.loc[:, 'predicted_input_roll']

        # rotations = pd.concat((player.data.pos_z, player.data.loc[frames_not_on_ground, 'rot_x':'rot_z'],
        #                        predicted_inputs), axis=1)

        player.controls = pd.concat((throttle, steer, pitch, yaw, roll, jump, boost, handbrake),
                                    axis=1)

    return






