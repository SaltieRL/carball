import logging
from typing import List

logger = logging.getLogger(__name__)


class GameInfo:
    def __init__(self):
        self.server_id = None
        self.server_name = None
        self.match_guid = None
        self.game_mode = None
        self.mutator_index = None
        self.rumble_mutator = None

    def parse_game_info_actor(self, actor_data: dict, game_event_actor: dict, objects: List[str]):
        """
        Parses game actor
        :param actor_data: game replication info
        :param game_event_actor: soccar game event actor
        :param objects: object list from the decompiled replay
        :return: self
        """        
        # There is no GameServerID if you play alone
        self.server_id = ''
        if 'ProjectX.GRI_X:GameServerID' in actor_data:
            self.server_id = actor_data['ProjectX.GRI_X:GameServerID']
        self.server_name = actor_data['Engine.GameReplicationInfo:ServerName']
        
        # A custom lobby doesn't have a MatchGUID
        self.match_guid = actor_data.get('ProjectX.GRI_X:MatchGUID', '')
        self.playlist = actor_data['ProjectX.GRI_X:ReplicatedGamePlaylist']
        self.mutator_index = actor_data.get('ProjectX.GRI_X:ReplicatedGameMutatorIndex', 0)

        if 'TAGame.GameEvent_Soccar_TA:SubRulesArchetype' in game_event_actor:
            # Only used for rumble stats
            # TODO can this contain any other mutators?
            self.rumble_mutator = objects[game_event_actor['TAGame.GameEvent_Soccar_TA:SubRulesArchetype']['actor']]

        logger.info('Created game info from actor')
        return self
