import numpy as np
import pandas as pd

T_r = -36.07956616966136  # torque coefficient for roll
T_p = -12.14599781908070  # torque coefficient for pitch
T_y = 8.91962804287785  # torque coefficient for yaw
D_r = -4.47166302201591  # drag coefficient for roll
D_p = -2.798194258050845  # drag coefficient for pitch
D_y = -1.886491900437232  # drag coefficient for yaw


def predict_user_inputs(ang_vels, rotations, deltas):
    delta_omega = -ang_vels.diff(-1)
    delta_omega = delta_omega[(delta_omega.T != 0).any()]  # Filter all-zero rows.
    tau = delta_omega.divide(deltas[delta_omega.index], axis='index')
    tau_vectors = np.expand_dims(tau.values, 2)

    rotation_matrices = get_rotation_matrices(rotations.loc[delta_omega.index])
    inverse_rotation_matrices: pd.Series = np.transpose(rotation_matrices)
    inverse_rotation_array = np.stack(inverse_rotation_matrices.values)

    tau_local = np.matmul(inverse_rotation_array, tau_vectors)

    ang_vel_vectors = np.expand_dims(ang_vels.loc[delta_omega.index].values, 2)
    omega_local = np.matmul(inverse_rotation_array, ang_vel_vectors)

    omega_and_tau_locals = np.concatenate([omega_local, tau_local], axis=1)

    rhs_and_omega = np.apply_along_axis(get_rhs_and_omega, 1, omega_and_tau_locals)

    u = np.apply_along_axis(get_u, 1, rhs_and_omega)
    controls_data_frame = pd.DataFrame(data=np.squeeze(u, 2),
                                       index=delta_omega.index,
                                       columns=['predicted_input_roll', 'predicted_input_pitch', 'predicted_input_yaw'])

    controls_data_frame.clip(-1, 1, inplace=True)
    return controls_data_frame


def get_rotation_matrices(rotations: pd.Series) -> pd.Series:
    pitch = rotations.rot_x
    yaw = rotations.rot_y
    roll = rotations.rot_z

    cos_roll = np.cos(roll).rename('cos_roll')
    sin_roll = np.sin(roll).rename('sin_roll')
    cos_pitch = np.cos(pitch).rename('cos_pitch')
    sin_pitch = np.sin(pitch).rename('sin_pitch')
    cos_yaw = np.cos(yaw).rename('cos_yaw')
    sin_yaw = np.sin(yaw).rename('sin_yaw')

    components: pd.DataFrame = pd.concat([cos_roll, sin_roll, cos_pitch, sin_pitch, cos_yaw, sin_yaw], axis=1)

    rotation_matrix = components.apply(get_rotation_matrix_from_row, axis=1, result_type='reduce')
    return rotation_matrix


def get_rotation_matrix_from_row(components: pd.Series) -> np.array:
    cos_roll, sin_roll, cos_pitch, sin_pitch, cos_yaw, sin_yaw = components.values
    rotation_matrix = np.array(
        [[cos_pitch * cos_yaw, cos_yaw * sin_pitch * sin_roll - cos_roll * sin_yaw,
          -cos_roll * cos_yaw * sin_pitch - sin_roll * sin_yaw],
         [cos_pitch * sin_yaw, sin_yaw * sin_pitch * sin_roll + cos_roll * cos_yaw,
          -cos_roll * sin_yaw * sin_pitch + sin_roll * cos_yaw],
         [sin_pitch, -cos_pitch * sin_roll, cos_pitch * cos_roll]])
    return rotation_matrix


def get_rhs_and_omega(omega_and_tau):
    omega = omega_and_tau[:3]
    tau = omega_and_tau[3:]
    return np.array([
        tau[0] - D_r * omega[0],
        tau[1] - D_p * omega[1],
        tau[2] - D_y * omega[2],
        omega[0],
        omega[1],
        omega[2]
    ])


def get_u(rhs_and_omega):
    rhs = rhs_and_omega[:3]
    omega = rhs_and_omega[3:]
    return np.array([
        rhs[0] / T_r,
        rhs[1] / (T_p + np.sign(rhs[1]) * omega[1] * D_p),
        rhs[2] / (T_y - np.sign(rhs[2]) * omega[2] * D_y)
    ])
