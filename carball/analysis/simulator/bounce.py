import numpy as np

R = 91.25
Y = 2.0
mu = 0.285
C_R = 0.6
A = 0.0003

GROUND_NORMAL = np.array([0, 0, 1])


def bounce(state, normal=GROUND_NORMAL):
    # pos = state.loc[:, ['x', 'y', 'z']].values
    # vel = state.loc[:, ['vx', 'vy', 'vz']].values
    # ang_vel = state.loc[:, ['rotvx', 'rotvy', 'rotvz']].values
    vel, ang_vel = state
    normal = normal.astype(float)
    ang_vel = ang_vel.astype(float)
    v_perp = np.dot(vel, normal) * normal
    v_para = vel - v_perp
    v_spin = R * np.cross(normal, ang_vel)
    s = v_para + v_spin

    ratio = np.sqrt(v_perp.dot(v_perp)) / np.sqrt(s.dot(s))

    delta_v_perp = - (1.0 + C_R) * v_perp
    delta_v_para = - min(1.0, Y * ratio) * mu * s

    new_state = (vel + delta_v_perp + delta_v_para,
                 ang_vel + A * R * np.cross(delta_v_para.astype(float), normal))
    return new_state
