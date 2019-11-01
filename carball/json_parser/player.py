import logging
from typing import TYPE_CHECKING, List

import numpy as np
import pandas as pd

from carball.json_parser.bots import get_bot_map, get_online_id_for_bot

if TYPE_CHECKING:
    from .team import Team

logger = logging.getLogger(__name__)
bot_map = get_bot_map()


class Player:

    def __init__(self):
        self.name = None
        self.online_id = None
        self.team = None  # using team class. set later.
        self.is_orange = None
        self.score = None
        self.goals = None
        self.assists = None
        self.saves = None
        self.shots = None
        self.is_bot = None

        self.frame_data = {}

        self.camera_settings = {}
        self.loadout = []
        self.paint = []
        self.user_colors = []

        self.data = None
        self.boosts = None
        self.demos = None

        self.title = None
        self.total_xp = None
        self.steering_sensitivity = None

        self.party_leader = None

    def __repr__(self):
        if self.team:
            return '%s: %s on %s' % (self.__class__.__name__, self.name, self.team)
        else:
            return '%s: %s' % (self.__class__.__name__, self.name)

    def create_from_actor_data(self, actor_data: dict, teams: List['Team']):
        self.name = actor_data['name']
        if 'Engine.PlayerReplicationInfo:bBot' in actor_data and actor_data['Engine.PlayerReplicationInfo:bBot']:
            self.is_bot = True
            self.online_id = get_online_id_for_bot(bot_map, self)

        else:
            actor_type = list(actor_data["Engine.PlayerReplicationInfo:UniqueId"]['unique_id']['remote_id'].keys())[0]
            self.online_id = actor_data["Engine.PlayerReplicationInfo:UniqueId"]['unique_id']['remote_id'][actor_type]
        try:
            self.score = actor_data["TAGame.PRI_TA:MatchScore"]
        except KeyError:
            logger.warning('Score is not found for player')
        team_actor_id = actor_data["Engine.PlayerReplicationInfo:Team"]
        if team_actor_id == -1:
            # if they leave at the end
            team_actor_id = actor_data['team']
        for team in teams:
            if team.actor_id == team_actor_id:
                self.is_orange = team.is_orange
        assert self.is_orange is not None, 'Cannot find team for player: %s' % self.name
        self.score = actor_data.get("TAGame.PRI_TA:MatchScore", None)
        self.goals = actor_data.get("TAGame.PRI_TA:MatchGoals", None)
        self.assists = actor_data.get("TAGame.PRI_TA:MatchAssists", None)
        self.saves = actor_data.get("TAGame.PRI_TA:MatchSaves", None)
        self.shots = actor_data.get("TAGame.PRI_TA:MatchShots", None)
        self.parse_actor_data(actor_data)

        logger.info('Created Player from actor_data: %s' % self)
        return self

    def parse_player_stats(self, player_stats: dict):
        self.name = player_stats["Name"]["value"]["str"]
        self.online_id = str(player_stats["OnlineID"]["value"]["q_word"])
        self.is_orange = bool(player_stats["Team"]["value"]["int"])
        self.score = player_stats["Score"]["value"]["int"]
        self.goals = player_stats["Goals"]["value"]["int"]
        self.assists = player_stats["Assists"]["value"]["int"]
        self.saves = player_stats["Saves"]["value"]["int"]
        self.shots = player_stats["Shots"]["value"]["int"]
        self.is_bot = bool(player_stats["bBot"]["value"]["bool"])

        logger.info('Created Player from stats: %s' % self)
        if self.is_bot or self.online_id == '0' or self.online_id == 0:
            self.online_id = get_online_id_for_bot(bot_map, self)

        return self

    def get_camera_settings(self, camera_data: dict):
        self.camera_settings['field_of_view'] = camera_data.get('fov', None)
        self.camera_settings['height'] = camera_data.get('height', None)
        self.camera_settings['pitch'] = camera_data.get('angle', None)
        self.camera_settings['distance'] = camera_data.get('distance', None)
        self.camera_settings['stiffness'] = camera_data.get('stiffness', None)
        self.camera_settings['swivel_speed'] = camera_data.get('swivel_speed', None)
        self.camera_settings['transition_speed'] = camera_data.get('transition_speed', None)

        for key, value in self.camera_settings.items():
            if value is None:
                logger.warning('Could not find ' + key + ' in camera settings for ' + self.name)
        logger.info('Camera settings for %s: %s' % (self.name, self.camera_settings))

    def parse_actor_data(self, actor_data: dict):
        """
        Adds stuff not found in PlayerStats metadata.
        PlayerStats is a better source of truth - as actor_data might not have been updated (e.g. for last assist)

        :param actor_data:
        :return:
        """
        self.get_loadout(actor_data)
        self.party_leader = actor_data.get('TAGame.PRI_TA:PartyLeader', None)
        try:
            if self.party_leader is not None and \
                    'party_leader' in self.party_leader and \
                    'id' in self.party_leader['party_leader']:
                leader_actor_type = list(self.party_leader['party_leader']['id'][0].keys())[0]
                self.party_leader = str(self.party_leader['party_leader']['id'][0][leader_actor_type])
            else:
                self.party_leader = None
        except KeyError:
            logger.warning('Could not set player party leader for:', self.name)
            self.party_leader = None
        self.title = actor_data.get('TAGame.PRI_TA:Title', None)
        self.total_xp = actor_data.get('TAGame.PRI_TA:TotalXP', None)
        self.steering_sensitivity = actor_data.get('TAGame.PRI_TA:SteeringSensitivity', None)
        return self

    def get_loadout(self, actor_data: dict):
        if "TAGame.PRI_TA:ClientLoadouts" in actor_data:  # new version (2 loadouts)
            loadout_data = actor_data["TAGame.PRI_TA:ClientLoadouts"]["loadouts"]
        else:
            try:
                loadout_data = {'0': actor_data["TAGame.PRI_TA:ClientLoadout"]["loadout"]}
            except KeyError:
                loadout_data = {'0': {}}
        for loadout_name, _loadout in loadout_data.items():
            self.loadout.append({
                'version': _loadout.get('version', None),
                'car': _loadout.get('body', None),
                'skin': _loadout.get('decal', None),
                'wheels': _loadout.get('wheels', None),
                'boost': _loadout.get('boost', _loadout.get('rocket_trail', None)),
                'antenna': _loadout.get('antenna', None),
                'topper': _loadout.get('topper', None),
                'engine_audio': _loadout.get('engine_audio', None),
                'trail': _loadout.get('trail', None),
                'goal_explosion': _loadout.get('goal_explosion', None),
                'banner': _loadout.get('banner', None),
                'avatar_border': _loadout.get('unknown5', None)
            })
        if 'TAGame.PRI_TA:ClientLoadoutsOnline' in actor_data:
            loadout_online = actor_data['TAGame.PRI_TA:ClientLoadoutsOnline']['loadouts_online']
            # Paints
            for team in ['blue', 'orange']:
                paint = {}
                user_color = {}
                team_loadout = loadout_online[team]
                items = [
                    'car', 'skin', 'wheels', 'boost', 'antenna', 'topper',
                    #  8 unknown items O.o
                    'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Unknown',
                    'trail', 'goal_explosion', 'banner',
                    'Unknown', 'Unknown', 'Unknown', 'avatar_border'
                ]
                for item_name, corresponding_item in zip(items, team_loadout):  # order is based on menu
                    for attribute in corresponding_item:
                        if attribute['object_name'] == 'TAGame.ProductAttribute_Painted_TA':
                            if 'painted_old' in attribute['value']:
                                paint[item_name] = attribute['value']['painted_old']['value']
                            else:
                                paint[item_name] = attribute['value']['painted_new']
                        elif attribute['object_name'] == 'TAGame.ProductAttribute_UserColor_TA':
                            # TODO handle 'user_color_old', looks like an ID like primary and accent colors
                            if 'user_color_new' in attribute['value']:
                                # rgb integer, 0xAARRGGBB, banners and avatar borders have different default values
                                user_color[item_name] = attribute['value']['user_color_new']
                self.paint.append({
                    'car': paint.get('body', None),
                    'skin': paint.get('decal', None),
                    'wheels': paint.get('wheels', None),
                    'boost': paint.get('boost', None),
                    'antenna': paint.get('antenna', None),
                    'topper': paint.get('topper', None),
                    'trail': paint.get('trail', None),
                    'goal_explosion': paint.get('goal_explosion', None),
                    'banner': paint.get('banner', None)
                })
                self.user_colors.append({
                    'banner': user_color.get('user_color', None),
                    'avatar_border': user_color.get('avatar_border', None)
                })
        logger.info('Loadout for %s: %s' % (self.name, self.loadout))

    def parse_data(self, _dict: dict):
        """
        ['ping', 'pos_x', 'pos_y', 'pos_z', 'rot_x', 'rot_y', 'rot_z', 'vel_x',
        'vel_y', 'vel_z', 'ang_vel_x', 'ang_vel_y', 'ang_vel_z', 'throttle',
        'steer', 'handbrake', 'ball_cam', 'dodge_active', 'double_jump_active',
        'jump_active', 'boost', 'boost_active', 'power_up', 'power_up_active']

        {'ang_vel_x': dtype('float64'),
         'ang_vel_y': dtype('float64'),
         'ang_vel_z': dtype('float64'),
         'ball_cam': dtype('O'),
         'boost': dtype('float64'),
         'boost_active': dtype('O'),
         'dodge_active': dtype('O'),
         'double_jump_active': dtype('O'),
         'handbrake': dtype('O'),
         'jump_active': dtype('O'),
         'ping': dtype('int64'),
         'pos_x': dtype('float64'),
         'pos_y': dtype('float64'),
         'pos_z': dtype('float64'),
         'rot_x': dtype('float64'),
         'rot_y': dtype('float64'),
         'rot_z': dtype('float64'),
         'steer': dtype('float64'),
         'throttle': dtype('float64'),
         'vel_x': dtype('float64'),
         'vel_y': dtype('float64'),
         'vel_z': dtype('float64'),
         'power_up': dtype('O'),
         'power_up_active': dtype('O')}

        :param _dict:
        :return:
        """
        self.data = pd.DataFrame.from_dict(_dict, orient='index')

    def get_data_from_car(self, car_data):
        if car_data is None:
            car_data = {'team_paint': {}}

        for i in range(2):
            # default blue primary = 35, default orange primary = 33, default accent = 0, default glossy = 270
            self.loadout[i]['primary_color'] = car_data['team_paint'].get(i, {}).get('primary_color', 35 if i == 0 else 33)
            self.loadout[i]['accent_color'] = car_data['team_paint'].get(i, {}).get('accent_color', 0)
            self.loadout[i]['primary_finish'] = car_data['team_paint'].get(i, {}).get('primary_finish', 270)
            self.loadout[i]['accent_finish'] = car_data['team_paint'].get(i, {}).get('accent_finish', 270)
