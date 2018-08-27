#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd

FRAME_DT = 0.016358
omega_max = 5.5
T_r = -36.07956616966136  # torque coefficient for roll
T_p = -12.14599781908070  # torque coefficient for pitch
T_y = 8.91962804287785  # torque coefficient for yaw
D_r = -4.47166302201591  # drag coefficient for roll
D_p = -2.798194258050845  # drag coefficient for pitch
D_y = -1.886491900437232  # drag coefficient for yaw

T = np.array([[T_r, 0, 0],
              [0, T_p, 0],
              [0, 0, T_y]])
T_inv = np.linalg.inv(T)


def convert_from_euler_angles(rotation):
    pitch, yaw, roll = rotation
    cos_r = np.cos(roll)
    sin_r = np.sin(roll)
    cos_p = np.cos(pitch)
    sin_p = np.sin(pitch)
    cos_y = np.cos(yaw)
    sin_y = np.sin(yaw)

    theta = np.array([[cos_p * cos_y, cos_p * sin_y, sin_p],
                      [cos_y * sin_p * sin_r - cos_r * sin_y, sin_y * sin_p * sin_r + cos_r * cos_y, -cos_p * sin_r],
                      [-cos_r * cos_y * sin_p - sin_r * sin_y, -cos_r * sin_y * sin_p + sin_r * cos_y, cos_p * cos_r]]
                     ).T

    return theta


def find_user_input(omega_t, omega_dt, rotation, dt=FRAME_DT):
    """
    ω(t + Δt) = ω(t) + τΔt

    τ = Θ (T u  + D Θ^T ω), where u = [[u_r], [u_p],[u_y]]

    and T = [[T_r, 0, 0], [0, T_p, 0], [0, 0, T_y]]
    and D = [[D_r, 0, 0], [0, D_p (1 - |u_p|), 0], [0, 0, D_y (1 - |u_y|)]]

    u = T^-1( Θ^T τ - D Θ^T ω),
    τ = (ω(t + Δt) - ω(t)) / Δt
    """
    omega_t = omega_t.reshape((3, 1))
    omega_dt = omega_dt.reshape((3, 1))

    D = np.array([[D_r, 0, 0], [0, D_p / 2, 0], [0, 0, D_y / 2]])

    Theta = convert_from_euler_angles(rotation)
    float_formatter = lambda x: "%.2f" % x
    np.set_printoptions(formatter={'float_kind': float_formatter})
    # print(Theta.dot(Theta.T))
    tau = (omega_dt - omega_t) / dt
    u = np.dot(T_inv, np.dot(Theta.T, tau) - np.dot(D, np.dot(Theta.T, omega_t)))

    """
    r * t_r + d_r * omega_r = tau_r
    p * t_p + d_p * omega_p * (1 - abs(p)) = tau_p
    y * t_y + d_y * omega_y * (1 - abs(y)) = tau_y

    r = (tau_r - d_r * omega_r) / t_r
    p = (tau_p - d_p * omega_p) / (t_p - d_p * omega_p) or  (tau_p - d_p * omega_p) / (t_p + d_p * omega_p)
    y = (tau_y - d_y * omega_y) / (t_y - d_y * omega_y)
    """

    u = np.clip(u, -1, 1)
    return u

def find_omega_dt(omega_t, rotation, user_input, dt=FRAME_DT):
    """
    τ = Θ (T u  + D Θ^T ω), where u = [[u_r], [u_p],[u_y]]
    """
    omega_t = omega_t.reshape((3, 1))
    input_roll, input_pitch, input_yaw = user_input

    Theta = convert_from_euler_angles(rotation)

    D = np.array([[D_r, 0, 0], [0, D_p * (1 - abs(input_pitch)), 0], [0, 0, D_y * (1 - abs(input_yaw))]])
    # D = np.array([[D_r, 0, 0], [0, D_p / 2, 0], [0, 0, D_y / 2]])
    u = np.array([[input_roll], [input_pitch], [input_yaw]])
    tau = np.dot(Theta, np.dot(T, u) + np.dot(D, np.dot(Theta.T, omega_t)))
    # print(tau)
    omega_dt = (omega_t + tau * dt).flatten()
    # print(omega_dt)

    omega_dt_magnitude = np.sqrt(omega_dt.dot(omega_dt))
    omega_dt *= np.fmin(1.0, omega_max / omega_dt_magnitude)
    return omega_dt


def import_data(file_index=None):
    column_headers = ["omega_x", "omega_y", "omega_z",
                      "rot_pitch", "rot_yaw", "rot_roll",
                      "input_roll", "input_pitch", "input_yaw"]

    files = ['roll_example.csv', 'pitch_example.csv', 'yaw_example.csv', 'rollpitchyaw_example.csv']
    if file_index is None:
        file_index = -1
    data = pd.read_csv(files[file_index],
                       header=None,
                       names=column_headers, dtype=np.float64)

    data.loc[:, 'rot_pitch': 'rot_roll'] *= np.pi / 32768.
    return data


def predict_user_inputs(ang_vels, rotations):
    predicted_inputs = {}

    # TODO: Optimise by vectorising.
    ang_vel_columns = ['ang_vel_x', 'ang_vel_y', 'ang_vel_z']
    rotation_columns = ['rot_x', 'rot_y', 'rot_z']
    for frame_number, row_data in ang_vels.iterrows():
        omega_t = row_data[ang_vel_columns].values
        try:
            omega_dt = ang_vels.loc[frame_number + 1, ang_vel_columns].values
        except KeyError:
            continue
        rotation = rotations.loc[frame_number, rotation_columns].values
        u = find_user_input(omega_t, omega_dt, rotation).flatten()
        # u = u[np.nonzero(u)]
        predicted_inputs[frame_number] = u

    predicted_df = pd.DataFrame.from_dict(predicted_inputs, orient='index')
    predicted_df.columns = ['predicted_input_roll', 'predicted_input_pitch', 'predicted_input_yaw']
    # print(predicted_df)

    # vectorised method
    # TODO: ACTUALLY VECTORISE.
    # omega_t = ang_vels.loc[:, ang_vel_columns].rename(
    #     columns={'ang_vel_x': 'omega_t_x', 'ang_vel_y': 'omega_t_y', 'ang_vel_z': 'omega_t_z'}
    # )
    # omega_dt = ang_vels.loc[:, ang_vel_columns].shift(1).rename(
    #     columns={'ang_vel_x': 'omega_dt_x', 'ang_vel_y': 'omega_dt_y', 'ang_vel_z': 'omega_dt_z'}
    # )
    # rotation = rotations.loc[:, rotation_columns] * np.pi
    # data_frame = pd.concat([omega_t, omega_dt, rotation], axis=1)
    # predicted_df_2 = data_frame[:5].apply(df_apply_find_user_input, axis=1, reduce=False)
    return predicted_df


def predict_omega_dt(file_index=None):
    data = import_data(file_index)
    predicted_omega_dts = {}

    for row_number, row_data in data.iterrows():
        omega_t = row_data['omega_x': 'omega_z'].values
        try:
            omega_dt = data.loc[row_number + 1, 'omega_x': 'omega_z'].values
        except KeyError:
            continue
        rotation = row_data.loc['rot_pitch':'rot_roll'].values
        user_input = row_data["input_roll": "input_yaw"]
        predicted_omega_dt = find_omega_dt(omega_t, rotation, user_input).flatten()

        predicted_omega_dts[row_number] = predicted_omega_dt
        # print(predicted_omega_dt)

        # diff = predicted_omega_dt - omega_dt
        # print(diff)
        # predicted_omega_dts[row_number] = diff

    predicted_df = pd.DataFrame.from_dict(predicted_omega_dts, orient='index')
    predicted_df.columns = ['predicted_omega_dt_x', 'predicted_omega_dt_y', 'predicted_omega_dt_z']
    data = pd.concat((data, predicted_df), axis=1)

    return data
