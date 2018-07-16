import numpy as np


def unrotate_positions(relative_positions, rotations):
    new_positions = relative_positions

    # YAW
    yaws = rotations[:, 1]
    yaws = -yaws * np.pi

    new_positions[:, 0], new_positions[:, 1] = new_positions[:, 0] * np.cos(yaws) - new_positions[:, 1] * np.sin(
        yaws), new_positions[:, 0] * np.sin(yaws) + new_positions[:, 1] * np.cos(yaws)

    # PITCH
    pitchs = rotations[:, 0]
    pitchs = pitchs * np.pi / 2

    new_positions[:, 2], new_positions[:, 0] = new_positions[:, 2] * np.cos(pitchs) - new_positions[:, 0] * np.sin(
        pitchs), new_positions[:, 2] * np.sin(pitchs) + new_positions[:, 0] * np.cos(pitchs)

    # ROLL
    rolls = rotations[:, 2]
    rolls = rolls * np.pi

    new_positions[:, 1], new_positions[:, 2] = new_positions[:, 1] * np.cos(rolls) - new_positions[:, 2] * np.sin(
        rolls), new_positions[:, 1] * np.sin(rolls) + new_positions[:, 2] * np.cos(rolls)

    return new_positions


def unrotate_position(relative_position, rotation):
    new_position = relative_position

    # YAW
    yaw = rotation[1]
    yaw = -yaw * np.pi

    new_position[0], new_position[1] = new_position[0] * np.cos(yaw) - new_position[1] * np.sin(yaw), new_position[
        0] * np.sin(yaw) + new_position[1] * np.cos(yaw)

    # PITCH

    pitch = rotation[0]
    pitch = pitch * np.pi / 2

    new_position[0], new_position[0] = new_position[2] * np.cos(pitch) - new_position[0] * np.sin(pitch), new_position[
        2] * np.sin(pitch) + new_position[0] * np.cos(pitch)

    # ROLL

    roll = rotation[2]
    roll = roll * np.pi

    new_position[1], new_position[2] = new_position[1] * np.cos(roll) - new_position[2] * np.sin(roll), new_position[
        1] * np.sin(roll) + new_position[2] * np.cos(roll)

    return new_position
