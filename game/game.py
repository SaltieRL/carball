import json
import pandas as pd
from datetime import datetime
from game.team import Team
from game.player import Player
from game.goal import Goal
from game.actor_parsing import BallActor, CarActor

BOOST_PER_SECOND = 80  # boost used per second out of 255


class Game:

    def __init__(self, file_path='', verbose=True, loaded_json=None):
        self.verbose = verbose

        self.file_path = file_path
        if loaded_json is None:
            with open(file_path, 'r') as f:
                self.replay = json.load(f)
        else:
            self.replay = loaded_json
        self.replay_data = self.replay['Frames']

        # set properties
        self.properties = self.replay['Properties']
        self.replay_id = self.replay['Properties']['Id']
        self.map = self.replay['Properties']['MapName']
        self.name = self.replay['Properties'].get('ReplayName', None)
        self.id = self.replay['Properties']["Id"]
        self.datetime = datetime.strptime(self.replay['Properties']['Date'], '%Y-%m-%d %H-%M-%S')
        # print(self.datetime)
        self.replay_version = self.replay['Properties']['ReplayVersion']

        self.teams = []
        self.players = self.create_players()
        self.goals = self.get_goals()

        self.all_data = self.parse_replay()

        self.frames = None
        self.ball = None
        self.demos = None
        self.parse_all_data(self.all_data)

    def __repr__(self):
        team_0_name = self.teams[0].name
        team_1_name = self.teams[1].name
        team_0_score = self.teams[0].score
        team_1_score = self.teams[1].score
        return "%s: %s vs %s (%s:%s)" % (self.name, team_0_name, team_1_name, team_0_score, team_1_score)

    def create_players(self):
        players = []
        for player_stats in self.replay["Properties"].get("PlayerStats", {}):
            player = Player().parse_player_stats(player_stats)
            players.append(player)
        return players

    def get_goals(self):
        goals = self.properties["Goals"]
        number_of_goals = len(goals)

        # find frame where time > time
        goal_number = 0
        frame_number = 0
        for frame in self.replay_data:
            frame_time = frame["Time"]
            # print(goal_number, number_of_goals)
            if frame_time > goals[goal_number]["Time"]:
                goals[goal_number]["FrameNumber"] = frame_number
                goal_number += 1
                if goal_number == number_of_goals:
                    break
            frame_number += 1

        if self.verbose:
            print('Found goals:', goals)

        goals = []
        for goal_dict in self.properties["Goals"]:
            goal = Goal(goal_dict, self)
            goals.append(goal)
        return goals

    def parse_replay(self):
        """
        :return: all_data = {
            'player_ball_data': player_ball_data,
            'player_dicts': player_dicts,
            'team_dicts': team_dicts,
            'frames_data': frames_data,
            'cameras_data': cameras_data
            'demos_data': demos_data
        }

        !!! ALL INPUTS AND OUTPUTS NOW IN DATA !!!
        player_ball_data format:
        {player_actor_id: {
            'inputs': {frame_number: {pos_x, pos_y ...}, f_no2: {...} ...,}
            'outputs': [[throttle, steer, 'pitch', yaw, roll, jump, boost, handbrake]]
        }}
        currently implemented:
            inputs: posx, posy, posz, rotx, roty, rotz, vx, vy, vz, angvx, angy, angvz, boost_amt
            outputs: throttle, steer, handbrake, boost, jump, doublejump, dodge

        player_dicts  = {player_actor_id : {actor_data}, player_actor_id_2: {actor_data_2}}
        team_dicts = {team_actor_id: {actor_data, 'colour':'blue'/'orange', also includes name}
        frames_data = {frame_number: {time, delta, seconds_remaining, is_overtime, ball_has_been_hit}
        cameras_data = {player_actor_id: actor_data}
        demos_data = {frame_number: demolish_data}

        """
        player_ball_data = {'ball': {}}

        # dictionaries to contain data in frames
        player_dicts = {}  # player_actor_id: player_dict
        team_dicts = {}

        player_car_ids = {}  # player_actor_id: car_actor_id
        car_player_ids = {}  # car_actor_id: player_actor_id
        # car_linked_ids = {}  # car_actor_id: {'player', 'jump, doublejump, '}

        current_actor_ids = []
        current_actors = {}  # id:actor_update

        # stores car_actor_ids to collect data for at each frame
        current_car_ids_to_collect = []

        frames = self.replay_data
        frames_data = {}
        soccar_game_event_actor_id = None
        frame_number = 0
        last_goal_frame_number = self.goals[-1].frame_number
        current_goal_number = 0

        cameras_data = {}  # player_actor_id: actor_data
        demos_data = []  # frame_number: demolish_data

        # loop through frames
        for frame in frames:
            # # don't bother after last goal
            # if frame_number > last_goal_frame_number:
            #     break

            _f_time = frame["Time"]
            _f_delta = frame["Delta"]
            # print(frame_number, _f_time)

            # remove deleted actors
            for deleted_actor_id in frame["DeletedActorIds"]:
                current_actor_ids.remove(deleted_actor_id)
                current_actors.pop(deleted_actor_id)
                if deleted_actor_id in car_player_ids:
                    player_actor_id = car_player_ids[deleted_actor_id]
                    if len(car_player_ids) != len(player_car_ids):
                        x = 1
                    car_player_ids.pop(deleted_actor_id)
                    try:
                        player_car_ids.pop(player_actor_id)
                    except KeyError:
                        pass
            # apply actor updates
            for actor_update in frame["ActorUpdates"]:
                actor_id = actor_update["Id"]

                # add if new actor
                if actor_id not in current_actor_ids:
                    current_actor_ids.append(actor_id)
                    current_actors[actor_id] = actor_update
                else:
                    # update stuff in current_actors
                    for _k, _v in actor_update.items():
                        current_actors[actor_id][_k] = _v

            # find players and ball
            for actor_id, actor_data in current_actors.items():
                if actor_data[
                    "TypeName"] == "TAGame.Default__PRI_TA" and "Engine.PlayerReplicationInfo:Team" in actor_data:
                    player_dict = {
                        'name': actor_data["Engine.PlayerReplicationInfo:PlayerName"],
                        'team': actor_data["Engine.PlayerReplicationInfo:Team"],
                        # 'steam_id': actor_data["Engine.PlayerReplicationInfo:UniqueId"]["SteamID64"],
                        # 'player_id': actor_data["Engine.PlayerReplicationInfo:PlayerID"]
                    }
                    if actor_id not in player_dicts:
                        # add new player
                        player_dicts[actor_id] = player_dict
                        if self.verbose:
                            print('Found player: %s (id: %s)' %
                                  (player_dict['name'], actor_id))
                        player_ball_data[actor_id] = {}
                    else:
                        # update player_dicts
                        for _k, _v in actor_data.items():
                            player_dicts[actor_id][_k] = _v
                elif actor_data["ClassName"] == "TAGame.Team_Soccar_TA":
                    team_dicts[actor_id] = actor_data
                    team_dicts[actor_id]['colour'] = 'blue' if actor_data[
                                                                   "TypeName"] == "Archetypes.Teams.Team0" else 'orange'
                # elif actor_data["TypeName"] == "Archetypes.Ball.Ball_Default":
                #     player_ball_data['ball'] = {}

            # stop data collection after goal
            try:
                if frame_number > self.goals[current_goal_number].frame_number:
                    # set all players to sleeping after goal
                    for car_actor_id in car_player_ids:
                        current_actors[car_actor_id][
                            "TAGame.RBActor_TA:ReplicatedRBState"]['Sleeping'] = True
                    current_goal_number += 1
            except IndexError:
                # after last goal.
                pass
            # gather data at this frame
            if _f_delta != 0:
                # frame stuff
                frame_data = {
                    'time': frame["Time"],
                    'delta': frame["Delta"],
                }
                if soccar_game_event_actor_id is None:
                    # set soccar_game_event_actor_id
                    for actor_id, actor_data in current_actors.items():
                        if actor_data["TypeName"] == "Archetypes.GameEvent.GameEvent_Soccar":
                            soccar_game_event_actor_id = actor_id
                            break
                frame_data['seconds_remaining'] = current_actors[soccar_game_event_actor_id].get(
                    "TAGame.GameEvent_Soccar_TA:SecondsRemaining", 300)
                frame_data['is_overtime'] = current_actors[soccar_game_event_actor_id].get(
                    "TAGame.GameEvent_Soccar_TA:bOverTime", False)
                frame_data['ball_has_been_hit'] = current_actors[soccar_game_event_actor_id].get(
                    "TAGame.GameEvent_Soccar_TA:bBallHasBeenHit", False)
                frames_data[frame_number] = frame_data
                # car and player stuff
                for actor_id, actor_data in current_actors.items():
                    if actor_data["TypeName"] == "Archetypes.Car.Car_Default" and \
                            "Engine.Pawn:PlayerReplicationInfo" in actor_data and \
                            "ActorId" in actor_data["Engine.Pawn:PlayerReplicationInfo"]:
                        player_actor_id = actor_data[
                            "Engine.Pawn:PlayerReplicationInfo"]["ActorId"]
                        # assign car player links
                        player_car_ids[player_actor_id] = actor_id
                        car_player_ids[actor_id] = player_actor_id

                        RBState = actor_data.get(
                            "TAGame.RBActor_TA:ReplicatedRBState", {})
                        car_is_driving = actor_data.get(
                            "TAGame.Vehicle_TA:bDriving", False)
                        car_is_sleeping = RBState.get(
                            'Sleeping', True)

                        # only collect data if car is driving and not
                        # sleeping
                        if car_is_driving and not car_is_sleeping:
                            current_car_ids_to_collect.append(actor_id)
                            # print(actor_id, player_actor_id)

                            data_dict = CarActor.get_data_dict(actor_data, version=self.replay_version)
                            # save data from here
                            player_ball_data[player_actor_id][frame_number] = data_dict

                        # get demo data
                        if "TAGame.Car_TA:ReplicatedDemolish" in actor_data:

                            demo_data = actor_data["TAGame.Car_TA:ReplicatedDemolish"]
                            # add attacker and victim player ids
                            attacker_car_id = demo_data["AttackerActorId"]
                            victim_car_id = demo_data["VictimActorId"]
                            if attacker_car_id != -1 and victim_car_id != -1:
                                # Filter out weird stuff where it's not a demo
                                # frame 1 of 0732D41D4AF83D610AE2A988ACBC977A (rlcs season 4 eu)
                                attacker_player_id = car_player_ids[attacker_car_id]
                                victim_player_id = car_player_ids[victim_car_id]
                                demo_data["attacker_player_id"] = attacker_player_id
                                demo_data["victim_player_id"] = victim_player_id
                                # add frame_number
                                demo_data['frame_number'] = frame_number
                                demos_data.append(demo_data)
                                # print(attacker_player_id, victim_player_id)
                                # print(player_dicts[attacker_player_id]['name'],
                                #       player_dicts[victim_player_id]['name'])
                                actor_data.pop("TAGame.Car_TA:ReplicatedDemolish")

                    elif actor_data["TypeName"] == "Archetypes.Ball.Ball_Default":
                        RBState = actor_data.get(
                            "TAGame.RBActor_TA:ReplicatedRBState", {})
                        # ball_is_sleeping = RBState.get('Sleeping', True)
                        data_dict = BallActor.get_data_dict(actor_data, version=self.replay_version)
                        player_ball_data['ball'][frame_number] = data_dict

                for actor_id, actor_data in current_actors.items():
                    if actor_data["TypeName"] == "TAGame.Default__CameraSettingsActor_TA" and \
                            "TAGame.CameraSettingsActor_TA:PRI" in actor_data:
                        try:
                            player_actor_id = actor_data["TAGame.CameraSettingsActor_TA:PRI"][1]
                        except KeyError:
                            # older version (RLCS S4)
                            player_actor_id = actor_data["TAGame.CameraSettingsActor_TA:PRI"]["ActorId"]
                        # add camera settings
                        if player_actor_id not in cameras_data and \
                                "TAGame.CameraSettingsActor_TA:ProfileSettings" in actor_data:
                            cameras_data[player_actor_id] = actor_data["TAGame.CameraSettingsActor_TA:ProfileSettings"]
                        # add ball cam to inputs
                        ball_cam = actor_data.get("TAGame.CameraSettingsActor_TA:bUsingSecondaryCamera", False)
                        try:
                            player_ball_data[player_actor_id][frame_number]['ball_cam'] = ball_cam
                        except KeyError:
                            # key error due to frame no not in inputs
                            # ignore as no point knowing
                            pass
                    elif actor_data["TypeName"] == "Archetypes.CarComponents.CarComponent_Boost":
                        car_actor_id = actor_data.get(
                            "TAGame.CarComponent_TA:Vehicle", None)
                        if car_actor_id is not None:
                            car_actor_id = car_actor_id["ActorId"]

                            if car_actor_id in current_car_ids_to_collect:
                                player_actor_id = car_player_ids[car_actor_id]
                                # boost_is_active = actor_data.get(
                                #     "TAGame.CarComponent_TA:Active", False)
                                boost_is_active = actor_data.get(
                                    "TAGame.CarComponent_TA:Active",
                                    actor_data.get("TAGame.CarComponent_TA:ReplicatedActive", False))
                                if boost_is_active:
                                    # manually decrease car boost amount (not shown in replay)
                                    # i assume game calculates the decrease itself similarly
                                    boost_amount = max(0,
                                                       actor_data[
                                                           "TAGame.CarComponent_Boost_TA:ReplicatedBoostAmount"] -
                                                       _f_delta * BOOST_PER_SECOND)
                                    actor_data["TAGame.CarComponent_Boost_TA:ReplicatedBoostAmount"] = boost_amount
                                    # actor_data["TAGame.CarComponent_Boost_TA:ReplicatedBoostAmount"] -= int(
                                    #     _f_delta * BOOST_PER_SECOND)
                                else:
                                    boost_amount = actor_data.get("TAGame.CarComponent_Boost_TA:ReplicatedBoostAmount",
                                                                  None)

                                player_ball_data[player_actor_id][frame_number]['boost'] = boost_amount
                                player_ball_data[player_actor_id][frame_number]['boost_active'] = boost_is_active
                    elif actor_data["TypeName"] == "Archetypes.CarComponents.CarComponent_Jump":
                        car_actor_id = actor_data.get(
                            "TAGame.CarComponent_TA:Vehicle", None)
                        if car_actor_id is not None:
                            car_actor_id = car_actor_id["ActorId"]
                            if car_actor_id in current_car_ids_to_collect:
                                player_actor_id = car_player_ids[car_actor_id]
                                # jump_is_active = actor_data.get(
                                #     "TAGame.CarComponent_TA:Active", False)
                                jump_is_active = actor_data.get(
                                    "TAGame.CarComponent_TA:Active",
                                    actor_data.get("TAGame.CarComponent_TA:ReplicatedActive", False))
                                player_ball_data[player_actor_id][frame_number]['jump_active'] = jump_is_active
                    elif actor_data["TypeName"] == "Archetypes.CarComponents.CarComponent_DoubleJump":
                        car_actor_id = actor_data.get(
                            "TAGame.CarComponent_TA:Vehicle", None)
                        if car_actor_id is not None:
                            car_actor_id = car_actor_id["ActorId"]
                            if car_actor_id in current_car_ids_to_collect:
                                player_actor_id = car_player_ids[car_actor_id]
                                # double_jump_is_active = actor_data.get(
                                #     "TAGame.CarComponent_TA:Active", False)
                                double_jump_is_active = actor_data.get(
                                    "TAGame.CarComponent_TA:Active",
                                    actor_data.get("TAGame.CarComponent_TA:ReplicatedActive", False))
                                player_ball_data[player_actor_id][frame_number][
                                    'double_jump_active'] = double_jump_is_active
                    elif actor_data["TypeName"] == "Archetypes.CarComponents.CarComponent_Dodge":
                        car_actor_id = actor_data.get(
                            "TAGame.CarComponent_TA:Vehicle", None)
                        if car_actor_id is not None:
                            car_actor_id = car_actor_id["ActorId"]
                            if car_actor_id in current_car_ids_to_collect:
                                player_actor_id = car_player_ids[car_actor_id]
                                # dodge_is_active = actor_data.get(
                                #     "TAGame.CarComponent_TA:Active", False)
                                dodge_is_active = actor_data.get(
                                    "TAGame.CarComponent_TA:Active",
                                    actor_data.get("TAGame.CarComponent_TA:ReplicatedActive", False))
                                player_ball_data[player_actor_id][frame_number]['dodge_active'] = dodge_is_active

                for player_actor_id in player_dicts:
                    actor_data = current_actors[player_actor_id]
                    if frame_number in player_ball_data[player_actor_id]:
                        player_ball_data[player_actor_id][frame_number]['ping'] = actor_data.get(
                            "Engine.PlayerReplicationInfo:Ping", None)
                    else:
                        player_ball_data[player_actor_id][frame_number] = {
                            'ping': actor_data.get("Engine.PlayerReplicationInfo:Ping", None)}

            current_car_ids_to_collect = []  # reset ids for next frame
            frame_number += 1

        all_data = {
            'player_ball_data': player_ball_data,
            'player_dicts': player_dicts,
            'team_dicts': team_dicts,
            'frames_data': frames_data,
            'cameras_data': cameras_data,
            'demos_data': demos_data
        }

        return all_data

    def parse_all_data(self, all_data):
        # TEAMS
        self.teams = []
        for team_id, team_data in all_data['team_dicts'].items():
            team = Team()
            team.parse_team_data(team_data)
            self.teams.append(team)

        # PLAYERS
        player_actor_id_player_dict = {}  # player_actor_id: Player
        for _player_actor_id, _player_data in all_data['player_dicts'].items():
            found_player = False
            for player in self.players:
                # if player leaves early, won't be created (as not found in metadata's player_stats)
                if _player_data['name'] == player.name:
                    player_actor_id_player_dict[_player_actor_id] = player
                    found_player = True
                    break
            if found_player:
                # just add extra stuff
                player.parse_actor_data(_player_data)
            else:
                # player not in endgame stats, create new player
                player = Player().create_from_actor_data(_player_data, self.teams)
                self.players.append(player)
                player_actor_id_player_dict[_player_actor_id] = player

            player.parse_data(all_data['player_ball_data'][_player_actor_id])
            # camera_settings might not exist (see 0AF8AC734890E6D3995B829E474F9924)
            player.get_camera_settings(all_data['cameras_data'].get(_player_actor_id, {}))

            for team in self.teams:
                if player.is_orange == team.is_orange:
                    team.add_player(player)

        # GOAL - add player if not found earlier (ie player just created)
        for goal in self.goals:
            if goal.player is None:
                goal.player = goal.get_player(self)

        # BALL
        self.ball = pd.DataFrame.from_dict(self.all_data['player_ball_data']['ball'], orient='index')

        # FRAMES
        self.frames = pd.DataFrame.from_dict(self.all_data['frames_data'], orient='index')

        # DEMOS
        self.demos = []
        for _demo_data in all_data['demos_data']:
            demo = {
                'frame_number': _demo_data['frame_number'],
                'attacker': player_actor_id_player_dict[_demo_data['attacker_player_id']],
                'victim': player_actor_id_player_dict[_demo_data['victim_player_id']],
                'attacker_vel': (_demo_data["AttackerVelocity"]["X"],
                                 _demo_data["AttackerVelocity"]["Y"],
                                 _demo_data["AttackerVelocity"]["Z"],),
                'victim_vel': (_demo_data["VictimVelocity"]["X"],
                               _demo_data["VictimVelocity"]["Y"],
                               _demo_data["VictimVelocity"]["Z"],),
            }
            self.demos.append(demo)

        del self.replay_data
        del self.replay
        del self.all_data
