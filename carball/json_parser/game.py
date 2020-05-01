import json
import logging
import re
from datetime import datetime
from typing import List

import pandas as pd

from .goal import Goal
from .player import Player
from .team import Team
from .game_info import GameInfo
from .frame_parser import parse_frames

logger = logging.getLogger(__name__)

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
        self.dropshot = None

    def initialize(self, file_path='', loaded_json=None, parse_replay: bool = True, clean_player_names: bool = False):
        """
        Initializes the Game object by processing the replay's json file, which finds and copies all relevant data.

        :param file_path: The (string) path to the replay's json file.
        :param loaded_json: The replay's json file.
        :param parse_replay: Boolean - should the replay be parsed?
        :param clean_player_names: Boolean - should the player names be cleared?
        """

        self.file_path = file_path
        if loaded_json is None:
            with open(file_path, 'r') as f:
                self.replay = json.load(f)
        else:
            self.replay = loaded_json

        logger.debug('Loaded JSON')

        self.replay_data = self.replay['network_frames']['frames']

        # set properties
        self.properties = self.replay['properties']
        self.replay_id = self.properties['Id']
        self.map = self.properties.get('MapName', 'Unknown')
        self.name = self.properties.get('ReplayName', None)
        self.match_type = self.properties['MatchType']
        self.team_size = self.properties['TeamSize']

        if self.name is None:
            logger.warning('Replay name not found')
        self.id = self.properties["Id"]

        date_string = self.properties['Date']
        for date_format in DATETIME_FORMATS:
            try:
                self.datetime = datetime.strptime(date_string, date_format)
                break
            except ValueError:
                pass
        else:
            logger.error('Cannot parse date: ' + date_string)

        self.replay_version = self.properties.get('ReplayVersion', None)
        logger.info(f"version: {self.replay_version}, date: {self.datetime}")
        if self.replay_version is None:
            logger.warning('Replay version not found')

        self.players: List[Player] = self.create_players()
        self.goals: List[Goal] = self.get_goals()
        self.primary_player: dict = self.get_primary_player()

        if parse_replay:
            self.all_data = parse_frames(self)
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
            for player_stats in self.properties["PlayerStats"]:
                player = Player().parse_player_stats(player_stats)
                players.append(player)
        except KeyError:
            pass
        return players

    def get_primary_player(self):
        owner_name = self.properties.get('PlayerName')
        if owner_name is not None:
            for player in self.players:
                if player.name == owner_name:
                    return {'name': owner_name, 'id': player.online_id}
            return {'name': owner_name, 'id': None}

    def get_goals(self) -> List[Goal]:
        """
        Gets goals from replay_properties and creates respective Goal objects.

        :return: List[Goal]
        """

        if "Goals" not in self.properties:
            return []

        goals = self.properties["Goals"]

        logger.info('Found %s goals.' % len(goals))
        logger.debug('Goals: %s' % goals)

        goals_list = []
        for goal_dict in goals:
            goal = Goal(goal_dict, self)
            goals_list.append(goal)
        return goals_list


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
                                                          self.replay['objects'])

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
                    found_player.parse_actor_data(_player_data, self.replay['objects'])  # just add extra stuff
                    break
            if found_player is None:
                # player not in endgame stats, create new player
                try:
                    found_player = Player().create_from_actor_data(_player_data, self.teams, self.replay['objects'])
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
            found_player.get_camera_settings(all_data['cameras_data'].get(_player_actor_id, {}))
            found_player.get_data_from_car(all_data['car_dicts'].get(_player_actor_id, None))

            for team in self.teams:
                if found_player.is_orange == team.is_orange:
                    team.add_player(found_player)

            if clean_player_names:
                cleaned_player_name = re.sub(r'[^\x00-\x7f]', r'', found_player.name).strip()  # Support ASCII only
                if cleaned_player_name != found_player.name:
                    logger.warning(
                        f"Cleaned player name to ASCII-only. From: {found_player.name} to: {cleaned_player_name}")
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
        demo_map = dict()
        for _demo_data in all_data['demos_data']:
            demo = {
                'frame_number': _demo_data['frame_number'],
                'attacker': player_actor_id_player_dict[_demo_data['attacker_player_id']],
                'victim': player_actor_id_player_dict[_demo_data['victim_player_id']],
                'attacker_vel': (_demo_data["attack_velocity"]["x"],
                                 _demo_data["attack_velocity"]["y"],
                                 _demo_data["attack_velocity"]["z"],),
                'victim_vel': (_demo_data["victim_velocity"]["x"],
                               _demo_data["victim_velocity"]["y"],
                               _demo_data["victim_velocity"]["z"],),
            }

            # Key created to prevent duplicate demo counts
            key = (int(_demo_data["attack_velocity"]["x"]) + int(_demo_data["attack_velocity"]["y"]) + int(_demo_data["attack_velocity"]["z"]) +
                   int(_demo_data["victim_velocity"]["x"]) + int(_demo_data["victim_velocity"]["y"]) + int(_demo_data["victim_velocity"]["z"]))
            Game.add_demo_to_map(key, demo, demo_map)

        self.demos = list(demo_map.values())

        # PARTIES
        self.parties = all_data['parties']

        # DROPSHOT EVENTS
        if 'dropshot_phase' in self.ball:
            self.ball['dropshot_phase'] = self.ball['dropshot_phase'].astype('int8')

        for column in self.frames.columns:
            if column.startswith('dropshot_tile'):
                self.frames[column] = self.frames[column].astype('int8')

        self.dropshot = {
            'damage_events': []
        }

        damage_events = all_data['dropshot']['damage_events']
        ball_events = all_data['dropshot']['ball_events']

        if len(damage_events) > 1:
            # sometimes damages can trickle over to the next frame, clean those up
            frames = list(damage_events.keys())

            i = 0
            while i < len(frames) - 1:
                if frames[i] + 1 == frames[i + 1] and damage_events[frames[i]][0] == damage_events[frames[i + 1]][0]:
                    ball_event = next(event for event in reversed(ball_events) if event['frame_number'] < frames[i])
                    ball_phase = ball_event['state']

                    first_frame = damage_events[frames[i]]
                    trickle_frame = frames[i + 1]

                    while trickle_frame in frames:
                        # check if the total damage of the two frames is not more than it could be
                        if (ball_phase == 1 and len(first_frame[1]) + len(damage_events[trickle_frame][1])) <= 7 or \
                                (ball_phase == 2 and len(first_frame[1]) + len(damage_events[trickle_frame][1]) <= 19):
                            first_frame[1].extend(damage_events[trickle_frame][1])
                            damage_events.pop(trickle_frame)
                            i += 1
                            trickle_frame += 1
                        else:
                            break
                i += 1

        for frame_number, damage in damage_events.items():
            self.dropshot['damage_events'].append({
                'frame_number': frame_number,
                'player': player_actor_id_player_dict[damage[0]],
                'tiles': damage[1]
            })

        damage_frames = set(damage_events.keys())
        self.dropshot['tile_frames'] = \
            {k: v for (k, v) in all_data['dropshot']['tile_frames'].items() if k in damage_frames}

        self.dropshot['ball_events'] = ball_events

        del self.replay_data
        del self.replay
        del self.all_data

    @staticmethod
    def add_demo_to_map(key, demo, demo_map):
        if key in demo_map:
            old_demo = demo_map[key]
            if demo['attacker'] == old_demo['attacker'] and demo['victim'] == old_demo['victim']:
                if demo['frame_number'] < old_demo['frame_number']:
                    demo_map[key] = demo
                return
            Game.add_demo_to_map(key + 1, demo, demo_map)
        else:
            demo_map[key] = demo
