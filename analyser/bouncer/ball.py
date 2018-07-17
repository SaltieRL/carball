import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from .bounce import bounce


BALL_RADIUS = 91.25
SIDE_WALL_DISTANCE = 4096
BACK_WALL_DISTANCE = 5140
CEILING_DISTANCE = 2044
CORNER_WALL_DISTANCE = 8000
GOAL_X = 892.75
GOAL_X = 950
GOAL_Z = 640
GOAL_Z = 750
GOAL_Z = 900
x = 590
# CURVE_RADIUS_1, CURVE_RADIUS_2, CURVE_RADIUS_3 = 520, 260, 190  # ramp radii
CURVE_RADIUS_1, CURVE_RADIUS_2, CURVE_RADIUS_3 = x, x / 2, 175  # ramp radii

CURVE_X_1 = SIDE_WALL_DISTANCE - CURVE_RADIUS_1
CURVE_X_2 = SIDE_WALL_DISTANCE - CURVE_RADIUS_2
CURVE_X_3 = SIDE_WALL_DISTANCE - CURVE_RADIUS_3
CURVE_Y_1 = BACK_WALL_DISTANCE - CURVE_RADIUS_1
# CURVE_Y_2 = BACK_WALL_DISTANCE - CURVE_RADIUS_2
CURVE_Y_3 = BACK_WALL_DISTANCE - CURVE_RADIUS_3
CURVE_Z_1 = CEILING_DISTANCE - CURVE_RADIUS_1
CURVE_Z_2 = CURVE_RADIUS_2
CURVE_Z_3 = CURVE_RADIUS_3

SIMULATION_FPS = 120
SIMULATION_SECONDS = 3


class Ball:
    gravity = 650  # uu/s2
    air_resistance = 0.0305  # % loss per second
    ball_max_speed = 6000
    ball_max_rotation_speed = 6

    def __init__(self, ball_data, is_orange):
        self.is_orange = is_orange
        self.ball_data = ball_data
        self.sim_vars = {'position': ball_data[['pos_x', 'pos_y', 'pos_z']].values,
                         'velocity': ball_data[['vel_x', 'vel_y', 'vel_z']].values / 10,
                         'rotation': ball_data[['rot_x', 'rot_y', 'rot_z']].values,
                         'ang_vel': ball_data[['ang_vel_x', 'ang_vel_y', 'ang_vel_z']].values / 1000,
                         }

        self.is_shot = False

    def get_is_shot(self):
        self.sim_data = self.predict_ball_positions()
        # if not self.is_shot:
        #     # plt.plot(sim_data)
        #     print(self.ball_data)
        #     self.plot_sim_data()
        return self.is_shot

    def predict_ball_positions(self):
        """
        Returns an array of time and position and velocity up to time=t.
        :param t: Number of seconds to simulate
        :return:
        """
        starting_x_v = np.concatenate((self.sim_vars['position'], self.sim_vars['velocity']))
        sim_data = self.simulate_time(0, SIMULATION_SECONDS, 1 / SIMULATION_FPS, self.step_dt,
                                      starting_x_v)
        return sim_data

    def simulate_time(self, start_time, end_time, time_step, step_func, starting_values):
        t_s = []
        x_vs = []
        av_s = []

        simulated_time = start_time
        latest_x_v = starting_values
        while simulated_time < end_time:
            # record values at current time
            t_s.append(simulated_time)
            x_vs.append(latest_x_v)
            av_s.append(self.sim_vars['ang_vel'])

            # move by dt
            derivatives = step_func(latest_x_v, simulated_time)
            latest_x_v[3:] = derivatives[:3]
            latest_x_v = latest_x_v + derivatives * time_step
            simulated_time += time_step
            # CHECK IF BALL IN GOAL
            if self.is_orange:
                if latest_x_v[1] < -BACK_WALL_DISTANCE:
                    self.is_shot = True
                    # return
            else:
                if latest_x_v[1] > BACK_WALL_DISTANCE:
                    self.is_shot = True
                    # return

        t_s = np.array(t_s)
        x_vs = np.array(x_vs)
        av_s = np.array(av_s)
        sim_data = pd.DataFrame(
            data=np.column_stack((t_s, x_vs, av_s)),
            columns=['t', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'rotvx', 'rotvy', 'rotvz']
        )
        return sim_data

    def step_dt(self, x_v, t):
        x = x_v[:3]
        v = x_v[3:]
        # calculate collisions
        collided = False
        # ramps
        # bottom y axis
        if x[1] > CURVE_Y_3 and x[2] < CURVE_Z_3 and abs(x[0]) > GOAL_X and \
                (abs(x[1]) - CURVE_Y_3) ** 2 + (x[2] - CURVE_Z_3) ** 2 > (CURVE_RADIUS_3 - BALL_RADIUS) ** 2:
            surface_vector = np.array([0, CURVE_Y_3 - x[1], CURVE_Z_3 - x[2]])
            normal_vector = surface_vector / np.sqrt(surface_vector.dot(surface_vector))
            # print(t, x, normal_vector, surface_vector)
            # print(t, 'y+ bottom')
            if self.check_if_ball_leaving(x_v, normal_vector):
                collided = True
        elif x[1] < -CURVE_Y_3 and x[2] < CURVE_Z_3 and abs(x[0]) > GOAL_X and \
                (abs(x[1]) - CURVE_Y_3) ** 2 + (x[2] - CURVE_Z_3) ** 2 > (CURVE_RADIUS_3 - BALL_RADIUS) ** 2:
            surface_vector = np.array([0, CURVE_Y_3 - x[1], CURVE_Z_3 - x[2]])
            normal_vector = surface_vector / np.sqrt(surface_vector.dot(surface_vector))
            # print(t, x, normal_vector, surface_vector)
            # print(t, 'y- bottom')
            if self.check_if_ball_leaving(x_v, normal_vector):
                collided = True
        # bottom x axis
        if x[0] > CURVE_X_2 and x[2] < CURVE_Z_2 and \
                (abs(x[0]) - CURVE_X_2) ** 2 + (x[2] - CURVE_Z_2) ** 2 > (CURVE_RADIUS_2 - BALL_RADIUS) ** 2:
            surface_vector = np.array([CURVE_X_2 - x[0], 0, CURVE_Z_2 - x[2]])
            normal_vector = surface_vector / np.sqrt(surface_vector.dot(surface_vector))
            # print(t, x, normal_vector, surface_vector)
            # print(t, 'x+ bottom')
            if self.check_if_ball_leaving(x_v, normal_vector):
                collided = True
        elif x[0] < -CURVE_X_2 and x[2] < CURVE_Z_2 and \
                (abs(x[0]) - CURVE_X_2) ** 2 + (x[2] - CURVE_Z_2) ** 2 > (CURVE_RADIUS_2 - BALL_RADIUS) ** 2:
            surface_vector = np.array([CURVE_X_2 - x[0], 0, CURVE_Z_2 - x[2]])
            normal_vector = surface_vector / np.sqrt(surface_vector.dot(surface_vector))
            # print(t, x, normal_vector, surface_vector)
            # print(t, 'x- bottom')
            if self.check_if_ball_leaving(x_v, normal_vector):
                collided = True
        # top y axis
        if x[1] > CURVE_Y_1 and x[2] > CURVE_Z_1 and abs(x[0]) > GOAL_X and \
                (abs(x[1]) - CURVE_Y_1) ** 2 + (x[2] - CURVE_Z_1) ** 2 > (CURVE_RADIUS_1 - BALL_RADIUS) ** 2:
            surface_vector = np.array([0, CURVE_Y_1 - x[1], CURVE_Z_1 - x[2]])
            normal_vector = surface_vector / np.sqrt(surface_vector.dot(surface_vector))
            # print(t, x, normal_vector, surface_vector)
            # print(t, 'y+ top')
            if self.check_if_ball_leaving(x_v, normal_vector):
                collided = True
        elif x[1] < -CURVE_Y_1 and x[2] > CURVE_Z_1 and abs(x[0]) > GOAL_X and \
                (abs(x[1]) - CURVE_Y_1) ** 2 + (x[2] - CURVE_Z_1) ** 2 > (CURVE_RADIUS_1 - BALL_RADIUS) ** 2:
            surface_vector = np.array([0, CURVE_Y_1 - x[1], CURVE_Z_1 - x[2]])
            normal_vector = surface_vector / np.sqrt(surface_vector.dot(surface_vector))
            # print(t, x, normal_vector, surface_vector)
            # print(t, 'y- top')
            if self.check_if_ball_leaving(x_v, normal_vector):
                collided = True
        # top x axis
        if x[0] > CURVE_X_1 and x[2] > CURVE_Z_1 and \
                (abs(x[0]) - CURVE_X_1) ** 2 + (x[2] - CURVE_Z_1) ** 2 > (CURVE_RADIUS_1 - BALL_RADIUS) ** 2:
            surface_vector = np.array([CURVE_X_1 - x[0], 0, CURVE_Z_1 - x[2]])
            normal_vector = surface_vector / np.sqrt(surface_vector.dot(surface_vector))
            # print(t, x, normal_vector, surface_vector)
            # print(t, 'x+ top')
            if self.check_if_ball_leaving(x_v, normal_vector):
                collided = True
        elif x[0] < -CURVE_X_1 and x[2] > CURVE_Z_1 and \
                (abs(x[0]) - CURVE_X_1) ** 2 + (x[2] - CURVE_Z_1) ** 2 > (CURVE_RADIUS_1 - BALL_RADIUS) ** 2:
            surface_vector = np.array([CURVE_X_2 - x[0], 0, CURVE_Z_1 - x[2]])
            normal_vector = surface_vector / np.sqrt(surface_vector.dot(surface_vector))
            # print(t, x, normal_vector, surface_vector)
            # print(t, 'x- top')
            if self.check_if_ball_leaving(x_v, normal_vector):
                collided = True
        if x[2] < BALL_RADIUS:
            # floor
            normal_vector = np.array([0, 0, 1])
            if self.check_if_ball_leaving(x_v, normal_vector):
                collided = True
        elif x[2] > CEILING_DISTANCE - BALL_RADIUS:
            # ceiling
            normal_vector = np.array([0, 0, -1])
            if self.check_if_ball_leaving(x_v, normal_vector):
                collided = True
        # sides
        if x[0] < -SIDE_WALL_DISTANCE + BALL_RADIUS:
            normal_vector = np.array([1, 0, 0])
            if self.check_if_ball_leaving(x_v, normal_vector):
                collided = True
        elif x[0] > SIDE_WALL_DISTANCE - BALL_RADIUS:
            normal_vector = np.array([-1, 0, 0])
            if self.check_if_ball_leaving(x_v, normal_vector):
                collided = True
        # back
        if x[1] < -BACK_WALL_DISTANCE + BALL_RADIUS and \
                BALL_RADIUS < x[2] < CEILING_DISTANCE - BALL_RADIUS and \
                (abs(x[0]) > GOAL_X - BALL_RADIUS or abs(x[2]) > GOAL_Z - BALL_RADIUS):
            normal_vector = np.array([0, 1, 0])
            if self.check_if_ball_leaving(x_v, normal_vector):
                collided = True
        elif x[1] > BACK_WALL_DISTANCE - BALL_RADIUS and \
                BALL_RADIUS < x[2] < CEILING_DISTANCE - BALL_RADIUS and \
                (abs(x[0]) > GOAL_X - BALL_RADIUS or abs(x[2]) > GOAL_Z - BALL_RADIUS):
            normal_vector = np.array([0, -1, 0])
            if self.check_if_ball_leaving(x_v, normal_vector):
                collided = True

        # corner side
        if abs(x[0]) + abs(x[1]) + BALL_RADIUS > CORNER_WALL_DISTANCE:
            over_rt2 = 1 / np.sqrt(2)
            if x[0] < 0 and x[1] < 0:
                normal_vector = np.array([over_rt2, over_rt2, 0])
                if self.check_if_ball_leaving(x_v, normal_vector):
                    collided = True
            elif x[0] < 0 and x[1] > 0:
                normal_vector = np.array([over_rt2, -over_rt2, 0])
                if self.check_if_ball_leaving(x_v, normal_vector):
                    collided = True
            elif x[0] > 0 and x[1] < 0:
                normal_vector = np.array([-over_rt2, over_rt2, 0])
                if self.check_if_ball_leaving(x_v, normal_vector):
                    collided = True
            elif x[0] > 0 and x[1] > 0:
                normal_vector = np.array([-over_rt2, -over_rt2, 0])
                if self.check_if_ball_leaving(x_v, normal_vector):
                    collided = True

        if collided:
            state = (v, self.sim_vars['ang_vel'])
            new_state = bounce(state, normal_vector)
            v, self.sim_vars['ang_vel'] = new_state
            x_v[3:] = v

        # if v > max speed: v = v
        if v.dot(v) > self.ball_max_speed ** 2:
            v = v / np.sqrt(v.dot(v)) * self.ball_max_speed

        # calculate a
        a = np.array([0, 0, -self.gravity]) - self.air_resistance * v

        # if ang_vel > max rotation: normalise to 6
        ang_vel = self.sim_vars['ang_vel']
        if ang_vel.dot(ang_vel) > self.ball_max_rotation_speed ** 2:
            ang_vel = ang_vel / np.sqrt(ang_vel.dot(ang_vel)) * self.ball_max_rotation_speed
            self.sim_vars['ang_vel'] = ang_vel

        return np.concatenate((v, a)).flatten()

    def check_if_ball_leaving(self, x_v, normal_vector):
        if normal_vector.dot(x_v[3:6]) < 0:
            return True
        else:
            return False


def check_ball_collision(ball_position):
    ADJUSTED_BALL_RADIUS = BALL_RADIUS + 10
    collided = False
    if ball_position[1] > CURVE_Y_3 and ball_position[2] < CURVE_Z_3 and abs(ball_position[0]) > GOAL_X and \
            (abs(ball_position[1]) - CURVE_Y_3) ** 2 + (ball_position[2] - CURVE_Z_3) ** 2 > (
            CURVE_RADIUS_3 - ADJUSTED_BALL_RADIUS) ** 2:
        # print(t, ball_position, normal_vector, surface_vector)
        # print(t, 'y+ bottom')
        collided = True
    elif ball_position[1] < -CURVE_Y_3 and ball_position[2] < CURVE_Z_3 and abs(ball_position[0]) > GOAL_X and \
            (abs(ball_position[1]) - CURVE_Y_3) ** 2 + (ball_position[2] - CURVE_Z_3) ** 2 > (
            CURVE_RADIUS_3 - ADJUSTED_BALL_RADIUS) ** 2:
        # print(t, ball_position, normal_vector, surface_vector)
        # print(t, 'y- bottom')
        collided = True
    # bottom ball_position axis
    if ball_position[0] > CURVE_X_2 and ball_position[2] < CURVE_Z_2 and \
            (abs(ball_position[0]) - CURVE_X_2) ** 2 + (ball_position[2] - CURVE_Z_2) ** 2 > (
            CURVE_RADIUS_2 - ADJUSTED_BALL_RADIUS) ** 2:
        # print(t, ball_position, normal_vector, surface_vector)
        # print(t, 'ball_position+ bottom')
        collided = True
    elif ball_position[0] < -CURVE_X_2 and ball_position[2] < CURVE_Z_2 and \
            (abs(ball_position[0]) - CURVE_X_2) ** 2 + (ball_position[2] - CURVE_Z_2) ** 2 > (
            CURVE_RADIUS_2 - ADJUSTED_BALL_RADIUS) ** 2:
        # print(t, ball_position, normal_vector, surface_vector)
        # print(t, 'ball_position- bottom')
        collided = True
    # top y axis
    if ball_position[1] > CURVE_Y_1 and ball_position[2] > CURVE_Z_1 and abs(ball_position[0]) > GOAL_X and \
            (abs(ball_position[1]) - CURVE_Y_1) ** 2 + (ball_position[2] - CURVE_Z_1) ** 2 > (
            CURVE_RADIUS_1 - ADJUSTED_BALL_RADIUS) ** 2:
        # print(t, ball_position, normal_vector, surface_vector)
        # print(t, 'y+ top')
        collided = True
    elif ball_position[1] < -CURVE_Y_1 and ball_position[2] > CURVE_Z_1 and abs(ball_position[0]) > GOAL_X and \
            (abs(ball_position[1]) - CURVE_Y_1) ** 2 + (ball_position[2] - CURVE_Z_1) ** 2 > (
            CURVE_RADIUS_1 - ADJUSTED_BALL_RADIUS) ** 2:
        # print(t, ball_position, normal_vector, surface_vector)
        # print(t, 'y- top')
        collided = True
    # top ball_position axis
    if ball_position[0] > CURVE_X_1 and ball_position[2] > CURVE_Z_1 and \
            (abs(ball_position[0]) - CURVE_X_1) ** 2 + (ball_position[2] - CURVE_Z_1) ** 2 > (
            CURVE_RADIUS_1 - ADJUSTED_BALL_RADIUS) ** 2:
        # print(t, ball_position, normal_vector, surface_vector)
        # print(t, 'ball_position+ top')
        collided = True
    elif ball_position[0] < -CURVE_X_1 and ball_position[2] > CURVE_Z_1 and \
            (abs(ball_position[0]) - CURVE_X_1) ** 2 + (ball_position[2] - CURVE_Z_1) ** 2 > (
            CURVE_RADIUS_1 - ADJUSTED_BALL_RADIUS) ** 2:
        # print(t, ball_position, normal_vector, surface_vector)
        # print(t, 'ball_position- top')
        collided = True
    if ball_position[2] < ADJUSTED_BALL_RADIUS:
        # floor
        collided = True
    elif ball_position[2] > CEILING_DISTANCE - ADJUSTED_BALL_RADIUS:
        # ceiling
        collided = True
    # sides
    if ball_position[0] < -SIDE_WALL_DISTANCE + ADJUSTED_BALL_RADIUS:
        collided = True
    elif ball_position[0] > SIDE_WALL_DISTANCE - ADJUSTED_BALL_RADIUS:
        collided = True
    # back
    if ball_position[1] < -BACK_WALL_DISTANCE + ADJUSTED_BALL_RADIUS and \
            ADJUSTED_BALL_RADIUS < ball_position[2] < CEILING_DISTANCE - ADJUSTED_BALL_RADIUS and \
            (abs(ball_position[0]) > GOAL_X - ADJUSTED_BALL_RADIUS or abs(
                ball_position[2]) > GOAL_Z - ADJUSTED_BALL_RADIUS):
        collided = True
    elif ball_position[1] > BACK_WALL_DISTANCE - ADJUSTED_BALL_RADIUS and \
            ADJUSTED_BALL_RADIUS < ball_position[2] < CEILING_DISTANCE - ADJUSTED_BALL_RADIUS and \
            (abs(ball_position[0]) > GOAL_X - ADJUSTED_BALL_RADIUS or abs(
                ball_position[2]) > GOAL_Z - ADJUSTED_BALL_RADIUS):
        collided = True

    # corner side
    if abs(ball_position[0]) + abs(ball_position[1]) + ADJUSTED_BALL_RADIUS > CORNER_WALL_DISTANCE:
        if ball_position[0] < 0 and ball_position[1] < 0:
            collided = True
        elif ball_position[0] < 0 and ball_position[1] > 0:
            collided = True
        elif ball_position[0] > 0 and ball_position[1] < 0:
            collided = True
        elif ball_position[0] > 0 and ball_position[1] > 0:
            collided = True

    return collided


if __name__ == '__main__':
    # file_name = "episode_000008.csv"
    # file_name = "episode_000003.csv"  # y+ bottom ramp
    # file_name = "episode_000012.csv"  # y+ bottom ramp
    # file_name = "episode_000010.csv"  # x- bottom
    # file_name = "episode_000015.csv"  # x- bottom
    # file_name = "episode_000029.csv"  # x- bottom
    # file_name = "episode_000035.csv"  # x- bottom
    # file_path = os.path.join(os.getcwd(), 'data', file_name)
    # Ball(file_path)

    for file_name in os.listdir(os.path.join(os.getcwd(), 'data')):
        if file_name.endswith('.csv'):
            file_path = os.path.join(os.getcwd(), 'data', file_name)
            # print(file_path)
            # start_time = time.time()
            Ball(file_path)
            # parse_duration = time.time() - start_time
            # print(parse_duration)
            # x = input('Press enter to continue...')

    # save_all_for_data()
