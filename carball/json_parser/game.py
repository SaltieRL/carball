import json
import logging
import re
from datetime import datetime
from typing import List, Dict

import pandas as pd

from .actor_parsing import BallActor, CarActor
from carball.generated.api.game_pb2 import mutators_pb2 as mutators
from .goal import Goal
from .player import Player
from .team import Team
from .game_info import GameInfo
from .frame_parser import FrameParser

logger = logging.getLogger(__name__)

COMPONENT_ACTIVE_KEY = "TAGame.CarComponent_TA:Active"
COMPONENT_REPLICATED_ACTIVE_KEY = "TAGame.CarComponent_TA:ReplicatedActive"
BOOST_PER_SECOND = 80 * 1 / .93  # boost used per second out of 255
DATETIME_FORMATS = [
    '%Y-%m-%d %H-%M-%S',
    '%Y-%m-%d:%H-%M'
]


class Game:

    def __init__(self):
        self.file_path = None
        self.replay = None
        self.properties = None
        self.replay_id = None
        self.map = None
        self.name = None
        self.id = None
        self.datetime = None
        self.replay_version = None

        self.replay_data = None

        self.teams: List[Team] = None  # Added in parse_all_data
        self.players: List[Player] = None
        self.goals: List[Goal] = None
        self.primary_player: dict = None
        self.all_data = None

        self.frames = None
        self.kickoff_frames = None
        self.ball = None
        self.ball_type = None
        self.demos = None
        self.parties = None

    def initialize(self, file_path='', loaded_json=None, parse_replay: bool = True, clean_player_names: bool = False):
        self.file_path = file_path
        if loaded_json is None:
            with open(file_path, 'r') as f:
                self.replay = json.load(f)
        else:
            self.replay = loaded_json
        logger.debug('Loaded JSON')

        self.replay_data = self.replay['content']['body']['frames']

        # set properties
        self.properties = self.replay['header']['body']['properties']['value']
        self.replay_id = self.find_actual_value(self.properties['Id']['value'])
        if 'MapName' in self.properties:
            self.map = self.find_actual_value(self.properties['MapName']['value'])
        else:
            self.map = 'Unknown'
        self.name = self.find_actual_value(self.properties.get('ReplayName', None))
        self.match_type = self.find_actual_value(self.properties['MatchType']['value'])
        self.team_size = self.find_actual_value(self.properties['TeamSize']['value'])

        if self.name is None:
            logger.warning('Replay name not found')
        self.id = self.find_actual_value(self.properties["Id"]['value'])

        date_string = self.properties['Date']['value']['str']
        for date_format in DATETIME_FORMATS:
            try:
                self.datetime = datetime.strptime(date_string, date_format)
                break
            except ValueError:
                pass
        else:
            logger.error('Cannot parse date: ' + date_string)

        self.replay_version = self.properties.get('ReplayVersion', {}).get('value', {}).get('int', None)
        logger.info(f"version: {self.replay_version}, date: {self.datetime}")
        if self.replay_version is None:
            logger.warning('Replay version not found')

        self.players: List[Player] = self.create_players()
        self.goals: List[Goal] = self.get_goals()
        self.primary_player: dict = self.get_primary_player()

        if parse_replay:
            self.all_data = self.parse_replay()
            self.parse_all_data(self.all_data, clean_player_names)
            logger.info("Finished parsing %s" % self)

    def __repr__(self):
        team_0_name = self.teams[0].name
        team_1_name = self.teams[1].name
        team_0_score = self.teams[0].score
        team_1_score = self.teams[1].score
        return "%s: %s vs %s (%s:%s)" % (self.name, team_0_name, team_1_name, team_0_score, team_1_score)

    def create_players(self) -> List[Player]:
        players = []
        try:
            for player_stats in self.properties["PlayerStats"]["value"]["array"]:
                player = Player().parse_player_stats(player_stats["value"])
                players.append(player)
        except KeyError:
            pass
        return players

    def get_primary_player(self):
        owner_name = self.properties.get('PlayerName')
        if owner_name is not None:
            owner_name = owner_name['value']['str']
            for player in self.players:
                if player.name == owner_name:
                    return {'name': owner_name, 'id': player.online_id}
            return {'name': owner_name, 'id': None}

    def get_goals(self) -> List[Goal]:
        if "Goals" not in self.properties:
            return []

        goals = [g['value'] for g in self.properties["Goals"]["value"]["array"]]

        logger.info('Found %s goals.' % len(goals))
        logger.debug('Goals: %s' % goals)

        goals_list = []
        for goal_dict in goals:
            goal = Goal(goal_dict, self)
            goals_list.append(goal)
        return goals_list

    @staticmethod
    def find_actual_value(value_dict: dict) -> dict or int or bool or str:
        types = ['int', 'boolean', 'string', 'byte', 'str', 'name', ('flagged_int', 'int')]
        if value_dict is None:
            return None
        if 'value' in value_dict:
            value_dict = value_dict['value']
        for _type in types:
            if isinstance(_type, str):
                if _type in value_dict:
                    return value_dict[_type]
            else:
                value = value_dict
                if _type[0] in value:
                    for type_str in _type:
                        value = value[type_str]
                    return value
        else:
            return value_dict

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

        player_ball_data format:
        {
        'ball': {frame_number: {pos_x, pos_y ...}, f_no2: {...} ...,}
        player_actor_id: {
            frame_number: {
                pos_x, pos_y ...,
                throttle, steer, ...,
                ping, ball_cam
            },
            f_no2: {...} ...,
        }

        currently implemented:
            inputs: posx, posy, posz, rotx, roty, rotz, vx, vy, vz, angvx, angy, angvz, boost_amt
            outputs: throttle, steer, handbrake, boost, jump, doublejump, dodge

        player_dicts  = {player_actor_id : {actor_data}, player_actor_id_2: {actor_data_2}}
        team_dicts = {team_actor_id: {actor_data, 'colour':'blue'/'orange', also includes name}
        frames_data = {frame_number: {time, delta, seconds_remaining, is_overtime, ball_has_been_hit}
        cameras_data = {player_actor_id: actor_data}
        demos_data = {frame_number: demolish_data}

        """
        parser = FrameParser(self.replay_data, self)
        parser.parse_frames()

        player_ball_data = parser.player_data
        player_ball_data['ball'] = parser.ball_data

        all_data = {
            'player_ball_data': player_ball_data,
            'player_dicts': parser.player_dicts,
            'team_dicts': parser.team_dicts,
            'frames_data': parser.frames_data,
            'cameras_data': parser.cameras_data,
            'demos_data': parser.demos_data,
            'game_info_actor': parser.game_info_actor,
            'soccar_game_event_actor': parser.soccar_game_event_actor,
            'parties': parser.parties
        }

        return all_data

    def parse_all_data(self, all_data, clean_player_names: bool) -> None:
        """
        Finishes parsing after frame-parsing is done.
        E.g. Adds players not found in MatchStats metadata
        :param all_data: Dict returned by parse_replay
        :return:
        """
        # GAME INFO
        self.game_info = GameInfo().parse_game_info_actor(all_data['game_info_actor'],
                                                          all_data['soccar_game_event_actor'],
                                                          self.replay['content']['body']['objects'])

        # TEAMS
        self.teams = []
        for team_id, team_data in all_data['team_dicts'].items():
            team = Team().parse_team_data(team_data)
            self.teams.append(team)

        # PLAYERS
        player_actor_id_player_dict = {}  # player_actor_id: Player
        for _player_actor_id, _player_data in all_data['player_dicts'].items():
            if "TAGame.PRI_TA:MatchScore" not in _player_data:
                logger.warning(f"Player {_player_data['name']} as player has no MatchScore.")

            found_player = None
            for player in self.players:
                # if player leaves early, won't be created (as not found in metadata's player_stats)
                if _player_data['name'] == player.name:
                    found_player = player
                    player_actor_id_player_dict[_player_actor_id] = found_player
                    found_player.parse_actor_data(_player_data)  # just add extra stuff
                    break
            if found_player is None:
                # player not in endgame stats, create new player
                try:
                    found_player = Player().create_from_actor_data(_player_data, self.teams)
                except KeyError as e:
                    # KeyError: 'Engine.PlayerReplicationInfo:Team'
                    # in `team_actor_id = actor_data["Engine.PlayerReplicationInfo:Team"]`
                    # Player never actually joins the game.
                    if 'Engine.PlayerReplicationInfo:Team' not in _player_data:
                        logger.warning(f"Ignoring player: {_player_data['name']} as player has no team.")
                        continue
                    raise e
                self.players.append(found_player)
                player_actor_id_player_dict[_player_actor_id] = found_player

                # check if any goals are playerless and belong to this newly-created player
                for goal in self.goals:
                    if not goal.player and goal.player_name == found_player.name:
                        goal.player = found_player

            found_player.parse_data(all_data['player_ball_data'][_player_actor_id])
            # camera_settings might not exist (see 0AF8AC734890E6D3995B829E474F9924)
            found_player.get_camera_settings(all_data['cameras_data'].get(_player_actor_id, {}).get('cam_settings', {}))

            for team in self.teams:
                if found_player.is_orange == team.is_orange:
                    team.add_player(found_player)

            if clean_player_names:
                cleaned_player_name = re.sub(r'[^\x00-\x7f]', r'', found_player.name).strip()  # Support ASCII only
                if cleaned_player_name != found_player.name:
                    logger.warning(f"Cleaned player name to ASCII-only. From: {found_player.name} to: {cleaned_player_name}")
                    found_player.name = cleaned_player_name

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
                'attacker_vel': (_demo_data["attacker_velocity"]["x"],
                                 _demo_data["attacker_velocity"]["y"],
                                 _demo_data["attacker_velocity"]["z"],),
                'victim_vel': (_demo_data["victim_velocity"]["x"],
                               _demo_data["victim_velocity"]["y"],
                               _demo_data["victim_velocity"]["z"],),
            }
            self.demos.append(demo)

        # PARTIES
        self.parties = all_data['parties']

        del self.replay_data
        del self.replay
        del self.all_data
