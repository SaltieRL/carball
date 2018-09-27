import logging

logger = logging.getLogger(__name__)


class GameInfo:
    def __init__(self):
        self.server_id = None
        self.server_name = None
        self.match_guid = None
        self.game_mode = None
        self.mutator_index = None

    def parse_game_info_actor(self, actor_data: dict):
        """
        Parses game actor
        :param actor_data: game replication info
        :return: self
        """        
        # There is no GameServerID if you play alone
        self.server_id = ''
        if 'ProjectX.GRI_X:GameServerID' in actor_data:
            self.server_id = str(actor_data['ProjectX.GRI_X:GameServerID']['q_word'])
        self.server_name = actor_data['Engine.GameReplicationInfo:ServerName']
        
        # A custom lobby doesn't have a MatchGUID
        self.match_guid = actor_data.get('ProjectX.GRI_X:MatchGUID', '')
        self.playlist = actor_data['ProjectX.GRI_X:ReplicatedGamePlaylist']
        self.mutator_index = actor_data.get('ProjectX.GRI_X:ReplicatedGameMutatorIndex', 0)

        logger.info('Created game info from actor')
        return self
